import Reply
import time
from Creater import Creater
import multiprocessing
import tweepy as twitter
from Resources import keys

auth = twitter.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.oa_key, keys.oa_secret)
api = twitter.API(auth)

client = twitter.Client(keys.bearer_token)

def tweet():
    # create a content and tweet it
    creater = Creater()
    while True:
        tweet_type = creater.get_type()
        if tweet_type is None:
            pass
        else:
            order = creater.create_order()
            creater.send_tweet(order)

        time.sleep(60)


class IDPrinter(twitter.StreamingClient):
    def on_tweet(self, tweet):
        try:
            curr_id = tweet.id
            curr_tweet = api.lookup_statuses(id=[tweet.id])
            user = curr_tweet[0]._json['user']['screen_name']
            print(f"new tweet: {tweet.text}")

            order = Reply.construct_conv_order(curr_id)
            Reply.send_reply(order, curr_id, user)
        except:
            print("Unknown error happened")

def reply():
    printer = IDPrinter(keys.bearer_token)
    while True:
        try:
            printer.filter()
        except:
            print("Error happened")
            continue

if __name__ == "__main__":
    print("Start of the program\n\n")
    processes = []
    p1 = multiprocessing.Process(target=tweet)
    p1.start()
    processes.append(p1)

    p2=multiprocessing.Process(target=reply)
    p2.start()
    processes.append(p2)

    for process in processes:
        process.join()

# printer = IDPrinter(keys.bearer_token)
# # printer.delete_rules('1554062634634203137')
# # printer.delete_rules('1554065083797741568')
# # printer.add_rules(twitter.StreamRule('@Justin_prg -from:Justin_prg'))
# print(printer.get_rules())





