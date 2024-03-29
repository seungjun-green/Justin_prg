'''
import Reply
import time
from Creater import Creater
import multiprocessing
import Twitter

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


def reply():
    # get the replies to its tweet, and reply to them
    while True:
        try:
            replies = Twitter.Twitter().get_replies()

            for i, curr_reply in enumerate(replies):
                curr_id, text, user = curr_reply
                order = Reply.construct_conv_order(curr_id)
                Reply.send_reply(order, curr_id, user)
                if i == 0:
                    Twitter.record["reply"]["lastReplied_id"] = curr_id
        except:
            Twitter.record["reply"]["firstTime"] = True
            print("Some error happened - reply")

        time.sleep(15)


if __name__ == "__main__":
    print("Start of the program\n\n")
    processes = []
    p1 = multiprocessing.Process(target=tweet)
    p1.start()
    processes.append(p1)

    p2 = multiprocessing.Process(target=reply)
    p2.start()
    processes.append(p2)

    for process in processes:
        process.join()

'''