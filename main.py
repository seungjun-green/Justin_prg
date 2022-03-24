import keys
import openai
import tweepy as twitter
import helper
import time
import multiprocessing

auth = twitter.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.oa_key, keys.oa_secret)
api = twitter.API(auth)
openai.api_key = keys.ai_key

def tweet():
    while True:
        tweet_type = helper.get_type()
        if tweet_type != None:
            orders, settings = helper.create_order(type)
            a, b, c, d, e = settings

            for order in orders:
                helper.send_tweet(order, a, b, c, d, e)
        else:
            pass

        time.sleep(60)

def reply():
    while True:
        replies = helper.get_replies()

        for i, reply in enumerate(replies):
            curr_id,text, user = reply
            helper.send_reply(helper.construct_order(curr_id),curr_id, user)
            if i==0:
                helper.Data.lastReplied_id = curr_id


        time.sleep(15)


def elon():
    while True:
        elons = helper.get_elons_tweets()

        for i, reply in enumerate(elons):
            curr_id, text, user = reply
            helper.send_reply(helper.construct_order(curr_id), curr_id, user)
            if i == 0:
                helper.Data.elon_last_id = curr_id

        time.sleep(15)


if __name__ == "__main__":
    print("Start of the program")
    processes = []
    p1 = multiprocessing.Process(target=tweet)
    p1.start()
    processes.append(p1)

    p2=multiprocessing.Process(target=reply)
    p2.start()
    processes.append(p2)

    p3 = multiprocessing.Process(target=elon)
    p3.start()
    processes.append(p3)

    for process in processes:
        process.join()
