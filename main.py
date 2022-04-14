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
    # create a content and tweet it
    while True:
        tweet_type = helper.get_type()
        if tweet_type != None:
            orders, settings = helper.create_order(tweet_type)
            a, b, c, d, e = settings

            for order in orders:
                helper.send_tweet(order, a, b, c, d, e)
        else:
            pass

        time.sleep(60)

def reply():
    # get the replies to its tweet, and reply to them
    while True:
        try:
            replies = helper.get_replies()

            for i, reply in enumerate(replies):
                curr_id,text, user = reply
                order, participants = helper.construct_conv_order(curr_id)
                helper.send_reply(order, participants,curr_id, user)
                if i==0:
                    helper.record["reply"]["lastReplied_id"] = curr_id
        except:
            helper.record["reply"]["firstTime"] = True
            print("Some error happened - reply")

        time.sleep(15)

def elon():
    # get recent tweets of elonmusk, and reply to it
    while True:
        for celb in helper.celbs:
            try:
                cleb_tweets = helper.get_celb_tweets(celb)
                for i, reply in enumerate(cleb_tweets):
                    curr_id, text, user = reply
                    order, participants = helper.construct_conv_order(curr_id)
                    helper.send_reply(order, participants, curr_id, user)
                    if i == 0:
                        helper.record[celb]["lastReplied_id"] = curr_id
            except:
                # this try and excpet block is to make program keep running even though some error happend
                helper.record[celb]["firstTime"] = True
                print("Some error happened - celb")

        time.sleep(15)

if __name__ == "__main__":
    print("Start of the program\n\n")
    processes = []
    # p1 = multiprocessing.Process(target=tweet)
    # p1.start()
    # processes.append(p1)

    p2=multiprocessing.Process(target=reply)
    p2.start()
    processes.append(p2)

    p3 = multiprocessing.Process(target=elon)
    p3.start()
    processes.append(p3)

    for process in processes:
        process.join()
