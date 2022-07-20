import helper
import time
from Creater import Creater

def tweet():
    # create a content and tweet it
    creater = Creater()
    while True:
        tweet_type = creater.get_type()
        if tweet_type == None:
            pass
        else:
            orders, settings = creater.create_order(tweet_type)
            a, b, c, d, e = settings
            for order in orders:
                creater.send_tweet(order, a, b, c, d, e)

        time.sleep(60)

def reply():
    # get the replies to its tweet, and reply to them
    while True:
        try:
            replies = helper.get_replies()

            for i, reply in enumerate(replies):
                curr_id, text, user = reply
                order, participants = helper.construct_conv_order(curr_id)
                helper.send_reply(order, participants,curr_id, user)
                if i==0:
                    helper.record["reply"]["lastReplied_id"] = curr_id
        except:
            helper.record["reply"]["firstTime"] = True
            print("Some error happened - reply")

        time.sleep(15)

# if __name__ == "__main__":
#     print("Start of the program\n\n")
#     processes = []
#     # p1 = multiprocessing.Process(target=tweet)
#     # p1.start()
#     # processes.append(p1)t
#
#     p2=multiprocessing.Process(target=reply)
#     p2.start()
#     processes.append(p2)
#
#     for process in processes:
#         process.join()


