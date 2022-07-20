import openai
import data
import tweepy as twitter
import re
from datetime import datetime
import keys

production = True
engine = "text-davinci-002"

record = {
    "reply": {"firstTime": True, "lastReplied_id": 0},
    "elonmusk": {"firstTime": True, "lastReplied_id": 0},
    "engineers_feed": {"firstTime": True, "lastReplied_id": 0},
    "tim_cook": {"firstTime": True, "lastReplied_id": 0},
    "lexfridman": {"firstTime": True, "lastReplied_id": 0}
}

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
    else:
        print("Content tweeted - Development mode\n")


def create_stop_seq(user):
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
    else:
        try:
            rd = api.mentions_timeline(since_id=record["reply"]["lastReplied_id"])
            if (len(rd) > 0):
                print(f"reply-second Time: {len(rd)}")
            for dot in rd:
                replies.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))
        except twitter.errors.TweepyException as e:
            print(f"[get_replies] (Second time) Twitter Error: {e}\n")


    return replies

def process_str(str):
    last = str.find('Friend:')
    if last==-1:
        return str
    else:
        return str[:last]
