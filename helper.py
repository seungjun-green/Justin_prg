import random
import openai
import data
from newsapi import NewsApiClient
import keys
from datetime import date,timedelta
import tweepy as twitter
import re
from datetime import datetime
import json
import time
from git import Repo
import git

production = False
engine = "text-davinci-002"
celbs_name = {
    "elonmusk":["elonmusk:", "Elon Musk:", "Elon:", "elon:"],
    "lexfridman": ["lexfridman","Lex"],
}

record = {
    "reply": {"firstTime": True, "lastReplied_id": 0},
    "elonmusk": {"firstTime": True, "lastReplied_id": 0},
    "engineers_feed": {"firstTime": True, "lastReplied_id": 0},
    "tim_cook": {"firstTime": True, "lastReplied_id": 0},
    "lexfridman": {"firstTime": True, "lastReplied_id": 0}
}


def git_push(changes):
    try:
        repo = Repo(".")
        repo.git.add(update=True)
        repo.index.commit(changes)
        origin = repo.remote(name='origin')
        origin.push()
    except git.GitError as e:
        print(f'error: {e}')

def update_json(type_, txt, error, func_name):
    file_name = f"{type_}_errors.json"
    with open(file_name) as json_file:
        errors = json.load(json_file)
        curr_date = date.today().strftime("%d/%m/%Y")
        curr_time = time.strftime("%H:%M:%S", time.localtime())
        errors[curr_date+'-'+curr_time] = {"curr": txt, "error": error, "func": func_name}

    with open(file_name, 'w') as f:
        json.dump(errors, f, indent=4)

    print(f"updated {file_name}")


def get_type():
    now = datetime.now().time().replace(second=0, microsecond=0)
    currH, currM = now.hour, now.minute
    curr = (currH, currM)
    if curr in data.dev_times:
        return 'dev'
    elif curr in data.joke_times:
        return 'joke'
    elif curr in data.news_times:
        return 'news'
    else:
        return None

def dev_order(tag):
    choices = [
    f"Give me your personal thought about {tag}?",
    f"Say as if you used {tag} for the first time",
    f"Say as if you really like {tag}",
    f" Say something negative thing about {tag} and one or more way to solve problem.",
    f"Say about {tag} as if you mastered it",
    f"Say as if you’re learning {tag} and going through some hardship"
    f"Ask a stupid question related to {tag}"
    f"Say anything related to {tag}"
    f"Any recent news on {tag}?"
    ]

    return random.choice(choices)

def get_random_word():
    response = openai.Completion.create(
  engine=engine,
  prompt="Give me a random noun word",
  temperature=0.66,
  max_tokens=64,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

    return response

def create_order(type):
    if type == 'dev':
        root = random.choice(list(data.tags.items()))
        selected_tag = random.choice(list(root[1]))
        return [dev_order(selected_tag)], (0.15,64,1,0,0)
    if type == "joke":
        topic= get_random_word()
        return [f"Make a joke about {topic} that gives punchline or make people view it in other view"], (0.5,150,1,0,0)
    if type=='news':
        newsapi = NewsApiClient(api_key=keys.news_key)
        today = date.today()
        yesterday = today - timedelta(1)
        end = today.strftime("%Y-%m-%d")
        start = yesterday.strftime("%Y-%m-%d")
        new_things = []
        recent_news = newsapi.get_everything(
            domains='cnbc.com',
            from_param=start,
            to=end,
            language='en',
            sort_by='relevancy',
            page=1)

        str=recent_news['articles'][0]['title']
        if str.endswith('CNBC'):
            str=str[:-7]

        return [f"Friend:Feel free to express your emotion on: {str}\nYou:"], (0.5,60,1,0.5,0)


auth = twitter.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.oa_key, keys.oa_secret)
api = twitter.API(auth)


def send_tweet(order, a,b,c,d,e):
    # only used for creating contents - news!
    result = ""
    count = 0
    print(f"the order is:\n {order}")

    # get the response
    try:
        while True:
            response = openai.Completion.create(
                engine=engine,
                prompt=order,
                temperature=a,
                max_tokens=b,
                top_p=c,
                frequency_penalty=d,
                presence_penalty=e,
                stop=["Friend:"]
            )

            count += 1
            result += response['choices'][0]['text']
            order += response['choices'][0]['text']
            if count == 3 or response['choices'][0]['text'] == '':
                break

        print(f"new tweet is {result}")
    except openai.error.OpenAIError as e:
        print(f"[send_tweet] openAI Error: {e}\n")
        update_json("openai", order, str(e), "send_tweet")
        #git_push("updated openai_errors")

    # tweet the result
    if production:
        try:
            # if result is longer than 280 characters
            if len(result) > 280:
                split_strings = []
                for index in range(0, len(result), 270):
                    split_strings.append(result[index: index + 270])

                for i, sub_str in enumerate(split_strings):
                    if i == 0:
                        api.update_status(sub_str)
                    else:
                        result = api.user_timeline(user_id='justin_prg', count=1)
                        recent_id = result[0]._json['id']
                        api.update_status(status=sub_str, in_reply_to_status_id=recent_id)

            # if result is shorter than 280 characters
            else:
                api.update_status(result)
            print('tweet-tweeted!')
        except twitter.errors.TweepyException as e:
            print(f"[send_tweet] Twitter Error: {e} \n")
            #update_json("tweet",result, str(e), "send_tweet")
            #git_push("updated tweet_errors")
    else:
        print("Content tweeted - Development mode\n")



def create_stop_seq(user):
    if user in celbs_name:
        return celbs_name[user]
    else:
        # replying feature
        return [f"{user}:", "You:"]



def send_reply(order,particpants,curr_id, user):
    result = ""
    count = 0
    stop = create_stop_seq(user)
    # get the response
    try:
        while True:
            response = openai.Completion.create(
                engine=engine,
                prompt=order,
                temperature=0.5,
                max_tokens=60,
                top_p=1,
                frequency_penalty=0.5,
                presence_penalty=0,
                stop=stop
            )

            count += 1
            result += response['choices'][0]['text']
            order += response['choices'][0]['text']
            if count == 3 or response['choices'][0]['text'] == '':
                break

        # tweet the result
        result = re.sub('@[a-zA-Z_0-9]*', '', result)
        taggins = ""
        for particpant in particpants:
            taggins+=f'{particpant} '

        result = taggins + result
        result = re.sub('\n', '', result)
        result=process_str(result)
        print(f"My Reply: {result}")
    except openai.OpenAIError as e:
        print(f"[send_reply] openAI Error: {e}")
        #update_json("openai", order, str(e), "send_reply")
        #git_push("updated openai_errors")

    # tweet the reply
    if production:
        try:
            if len(result) > 280:
                split_strings = []
                for index in range(0, len(result), 270):
                    split_strings.append(result[index: index + 270])

                for i, sub_str in enumerate(split_strings):
                    if i == 0:
                        api.update_status(status=sub_str, in_reply_to_status_id=curr_id)

                    else:
                        result = api.user_timeline(user_id='justin_prg', count=1)
                        recent_id = result[0]._json['id']
                        api.update_status(status=sub_str, in_reply_to_status_id=recent_id)

            # if result is shorter than 280 characters
            else:
                api.update_status(status=result, in_reply_to_status_id=curr_id)
                print("reply-tweeted! \n")
        except twitter.errors.TweepyException as e:
            print(f"[send_reply] Twitter Error: {e}\n")
            #update_json("tweet", result, str(e), "send_reply")
            #git_push("updated tweet_errors")
    else:
        print("reply tweeted - Development mode\n")


def construct_conv_order(tw_id):
    chats = []
    particpants = set()
    rd = api.get_status(id=tw_id)
    while True:
        try:
            data = rd[0]._json
        except:
            data = rd._json

        text = data['text']
        #text = re.sub('@[a-zA-Z_0-9]*', '', text)
        user = data['user']['screen_name']
        if user == 'Justin_prg':
            user = 'You'
        else:
            particpants.add(f'@{user}')

        chats.append(f"{user}:{text}")
        parent_id = data['in_reply_to_status_id']
        if parent_id is None:
            break

        rd = api.get_status(id=parent_id)
    # reverse chats
    chats.reverse()
    order = ""
    for chat in chats:
        chat = re.sub('\n', '', chat)
        chat += '\n'
        order += chat

    order+='You:'
    print("\n-------start of the order-------")
    print(order)
    print("-------end of the order-------\n")
    return order, particpants




def get_replies():
    replies = []
    if record["reply"]["firstTime"]:

        # len(rd) should be 1 all the time,no matter wgat, but due to some error of Twitter API which say there was any no recent tweet, added While True block
        # from the second time it is OK for such error happening. Because at first time it have to update recent id. Which will be used in second time
        try:
            rd = api.mentions_timeline(count=1)
            print(f"reply-first Time: {len(rd)}")
            for dot in rd:
                replies.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))
            record["reply"]["firstTime"] = False
        except twitter.errors.TweepyException as e:
            print(f"[get_replies] (First time) Twitter Error: {e}\n")
            #update_json("tweet","first time - get replies", str(e), "get_replies")
    else:
        try:
            rd = api.mentions_timeline(since_id=record["reply"]["lastReplied_id"])
            if (len(rd) > 0):
                print(f"reply-second Time: {len(rd)}")
            for dot in rd:
                replies.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))
        except twitter.errors.TweepyException as e:
            print(f"[get_replies] (Second time) Twitter Error: {e}\n")
            #update_json("tweet","second time - get replies", str(e), "get_replies")


    return replies

def get_celb_tweets(celb):
    elons=[]
    if record[celb]["firstTime"]:
        # len(rd) should be 1 all the time,no matter wgat, but due to some error of Twitter API which say there was any no recent tweet, added While True block
        # from the second time it is for such error happening. Because at first time it have to update recent id. Which will be used in secind time
        try:
            rd = api.user_timeline(screen_name=celb, count=1)
            print(f"{celb} - first Time: {len(rd)}")
            for dot in rd:
                elons.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))
            record[celb]["firstTime"] = False
        except twitter.errors.TweepyException as e:
            print(f"[get_elons_tweets] (First time) Twitter Error: {e}\n")
            #update_json("tweet", "first time - get elons tweet", str(e), "get_elos_tweets")
    else:
        try:
            rd = api.user_timeline(screen_name=celb, since_id=record[celb]["lastReplied_id"])
            if (len(rd) > 0):
                print(f"{celb} - second Time: {len(rd)}")


            for dot in rd:
                elons.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))

        except twitter.errors.TweepyException as e:
            print(f"[get_elons_tweets] (Second time) Twitter Error: {e}\n")
            #update_json("tweet", "second time - get elons tweet", str(e), "get_elos_tweets")

    return elons

def process_str(str):
    last = str.find('Friend:')
    if last==-1:
        return str
    else:
        return str[:last]


