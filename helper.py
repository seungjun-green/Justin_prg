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



engine = "text-davinci-002"

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

        for i in range(len(recent_news)):
            str=recent_news['articles'][i]['title']
            if str.endswith('CNBC'):
                str=str[:-7]

            str=f"Feel free to express your emotion on: {str}"
            new_things.append(str)

        return new_things, (0,150,1,0,0)
    # if type == 'elon':
    #     recent_tweets = get_recent_tweets('elonmusk')
    #     orders = []
    #     for tweet in recent_tweets:
    #         curr_order = "Friend:{tweet}\nYou:"
    #         orders.append(curr_order)
    #
    #     return orders, (0.5,150,1,0,0)


auth = twitter.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.oa_key, keys.oa_secret)
api = twitter.API(auth)


def send_tweet(order, a,b,c,d,e):
    result = ""
    count = 0
    print(f"the order is {order}")

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
                presence_penalty=e
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
        update_json("tweet",result, str(e), "send_tweet")
        #git_push("updated tweet_errors")

def send_reply(order,curr_id, user):
    result = ""
    count = 0

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
                stop=["You:"]
            )

            count += 1
            result += response['choices'][0]['text']
            order += response['choices'][0]['text']
            if count == 3 or response['choices'][0]['text'] == '':
                break

        # tweet the result
        result = f'@{user}' + ' ' + result
        result = re.sub('\n', '', result)
        result=process_str(result)
        print(f"My Reply: {result}")
    except openai.OpenAIError as e:
        print(f"[send_reply] openAI Error: {e}")
        update_json("openai", order, str(e), "send_reply")
        #git_push("updated openai_errors")

    # tweet the reply
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
        update_json("tweet", result, str(e), "send_reply")
        #git_push("updated tweet_errors")

def construct_order(tw_id):
    chats = []
    rd = api.get_status(id=tw_id)
    while True:
        try:
            data = rd[0]._json
        except:
            data = rd._json

        text = data['text']
        text = re.sub('@[a-zA-Z_0-9]*', '', text)
        user = data['user']['screen_name']
        if user == 'Justin_prg':
            user = 'You'
        else:
            user = 'Friend'

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
    print("-------start of the order-------")
    print(order)
    print("-------end of the order-------")
    return order

class Data:
    firstTime = True
    lastReplied_id = 0
    elon_last_id = 0
    elon_firstTime=True

def get_replies():
    replies = []
    if Data.firstTime:
        rd = api.mentions_timeline(count=1)
        print(f"reply-first Time: {len(rd)}")
        for dot in rd:
            replies.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))
        Data.firstTime = False
    else:
        rd = api.mentions_timeline(since_id=Data.lastReplied_id)
        print(f"reply-second Time: {len(rd)}")
        for dot in rd:
            replies.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))


    return replies

def get_elons_tweets():
    elons=[]
    if Data.elon_firstTime:
        rd = api.user_timeline(screen_name="elonmusk", count=1)
        print(f"elon - first Time: {len(rd)}")
        for dot in rd:
            if dot._json['in_reply_to_status_id'] is None:
                elons.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))
        Data.elon_firstTime = False
    else:
        rd = api.user_timeline(screen_name="elonmusk", since_id=Data.elon_last_id)
        print(f"elon - second Time: {len(rd)}")
        for dot in rd:
            if dot._json['in_reply_to_status_id'] is None:
                elons.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))

    return elons



def process_str(str):
    last = str.find('Friend:')
    if last==-1:
        return str
    else:
        return str[:last]


