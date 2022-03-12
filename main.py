import time
import keys
import openai
from datetime import datetime
import tweepy as twitter
import data
import helper
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

def tweet(type):

    orders, settings = helper.create_order(type)
    a,b,c,d,e = settings


    for order in orders:
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

            print('tweeted!')
            print(f'{result} \n')
        except:
            print("Error Happened \n")

def creating_contents():
    while True:
        tweet_type = get_type()
        if tweet_type != None:
            tweet(tweet_type)
        else:
            pass
        time.sleep(60)

def construct_reply(text):
    rd = text.split()[1:]
    processed_text = ' '.join(rd)

    response = openai.Completion.create(
        engine="text-davinci-001",
        prompt=processed_text,
        temperature=0.5,
        max_tokens=60,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0
    )

    return response['choices'][0]['text']

def reply_or_like():
    firstTime = True
    lastReplied_id = 0

    while True:
        replies = []
        if firstTime:
            rd = api.mentions_timeline(count=3)
            print(f"first Time: {len(rd)}")
            for dot in rd:
                replies.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))
            firstTime=False
        else:
            rd = api.mentions_timeline(since_id=lastReplied_id)
            print(f"second Time: {len(rd)}")
            for dot in rd:
                replies.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))

        for i, reply in enumerate(replies):
            curr_id,text, user = reply
            my_reply = construct_reply(text)
            my_reply = f'@{user}'+' ' + my_reply
            try:
                api.update_status(status=my_reply, in_reply_to_status_id=curr_id)
            except:
                print("already replied")

            if i==0:
                lastReplied_id = curr_id

        time.sleep(15)


if __name__ == "__main__":
    processes = []
    p1 = multiprocessing.Process(target=creating_contents)
    p1.start()
    processes.append(p1)

    p2=multiprocessing.Process(target=reply_or_like)
    p2.start()
    processes.append(p2)

    for process in processes:
        process.join()


'''
After you woke up, all the thing you need to do is checking whetehr program works well in a intended way

A. Creating contents
1. sending tweet at exact time
2. openAi create reasonable responses for - dev talk, joke, news
3. schedule for those 3 should be good
4. When tweet is longer than 280 characters,bot should tweet it using replying to the tweet feature


B. replying to people's tweet
1. Should check new reply for every 15 seconds
2. It should reply to recent replies(currently no maximum for every 15 seconds: 0 ~ 9999)
3. It should not reply to the already replied tweet(this could happen if ur runninig program again immideatly after shutting down)

C. FUTRE PLAN

From web get:
1. Get the openAI settings, tweet times, and Tags
2. number of maximum replies an hour(pseudo code not even started yet)

JSON files recording:
1. tweetd - type, text, time
2. replied - tweet, time
'''