import time
import keys
import openai
from datetime import datetime
import tweepy as twitter
import data
import helper
import re
import multiprocessing

auth = twitter.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.oa_key, keys.oa_secret)
api = twitter.API(auth)
openai.api_key = keys.ai_key

last_replied = 0

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

def send_tweet(order, a,b,c,d,e):
    result = ""
    count = 0
    order += '\n\n'

    # get the response
    while True:
        response = openai.Completion.create(
            engine="text-davinci-001",
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

    # tweet the result
    try:
        # if result is longer than 280 characters
        if len(result) > 280:
            split_strings = []
            for index in range(0, len(result), 270):
                split_strings.append(result[index: index + 270])

            for i, str in enumerate(split_strings):
                if i == 0:
                    api.update_status(str)
                else:
                    result = api.user_timeline(user_id='justin_prg', count=1)
                    recent_id = result[0]._json['id']
                    api.update_status(status=str, in_reply_to_status_id=recent_id)

        # if result is shorter than 280 characters
        else:
            api.update_status(result)
        print('tweet-tweeted!')
    except twitter.errors.TweepyException as e:
        print(f"Tweet - Error Happened: {e} \n")

def send_reply(order,curr_id, user):
    result = ""
    count = 0
    # get the response
    while True:
        response = openai.Completion.create(
            engine="text-davinci-001",
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
    print(f"{count}, the reply is {result}")
    try:
        if len(result) > 280:
            split_strings = []
            for index in range(0, len(result), 270):
                split_strings.append(result[index: index + 270])

            for i, str in enumerate(split_strings):
                if i == 0:
                    api.update_status(status=str, in_reply_to_status_id=curr_id)

                else:
                    result = api.user_timeline(user_id='justin_prg', count=1)
                    recent_id = result[0]._json['id']
                    api.update_status(status=str, in_reply_to_status_id=recent_id)

        # if result is shorter than 280 characters
        else:
            api.update_status(status=result, in_reply_to_status_id=curr_id)
            print("reply-tweeted!")
    except twitter.errors.TweepyException as e:
        print(f"reply-Error Happened {e}\n")


def creating_contents():
    while True:
        tweet_type = get_type()
        if tweet_type != None:
            tweet(tweet_type)
        else:
            pass
        time.sleep(60)

def tweet(type):
    orders, settings = helper.create_order(type)
    a,b,c,d,e = settings

    for order in orders:
        send_tweet(order,a,b,c,d,e)



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

def get_replies():
    replies = []
    if Data.firstTime:
        rd = api.mentions_timeline(count=1)
        print(f"first Time: {len(rd)}")
        for dot in rd:
            replies.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))
        Data.firstTime = False
    else:
        rd = api.mentions_timeline(since_id=Data.lastReplied_id)
        print(f"second Time: {len(rd)}")
        for dot in rd:
            replies.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))

    return replies


def process_str(str):
    last = str.find('Friend:')
    if last==-1:
        return str
    else:
        return str[:last]

def reply():
    while True:
        replies = get_replies()

        for i, reply in enumerate(replies):
            curr_id,text, user = reply
            try:
                send_reply(construct_order(curr_id),curr_id, user)
            except twitter.errors.TweepyException as e:
                print(f"reply func- Error {e} \n")

            if i==0:
                Data.lastReplied_id = curr_id

        time.sleep(15)


if __name__ == "__main__":
    processes = []
    # p1 = multiprocessing.Process(target=creating_contents)
    # p1.start()
    # processes.append(p1)

    p2=multiprocessing.Process(target=reply)
    p2.start()
    processes.append(p2)

    for process in processes:
        process.join()


