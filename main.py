import openai
import tweepy as twitter
import helper
import time
import multiprocessing
from testing import newss as keys

auth = twitter.OAuthHandler("CbiBlIQwIeDKdYmcwxfYNErYh", "s0dR9Mw8JVwQVz5CxYM2GkMoEUnfQR0evwGBU9nfIm0VEdHc9Q")
auth.set_access_token("1499630375756509184-hxzaVnIh0kgfukgTZQSsQeYwzS4loT", "yubSOxS0VCSguzG96PhiqaR0l1jL937kcJJejoJn6qqkx")
api = twitter.API(auth)
print(keys.consumer_key)
print(keys.consumer_secret)
print(keys.oa_key)
print(keys.oa_secret)
api.update_status("testing a new api key")
# openai.api_key = keys.ai_key
#
# def tweet():
#     # create a content and tweet it
#     while True:
#         tweet_type = helper.get_type()
#         if tweet_type != None:
#             orders, settings = helper.create_order(tweet_type)
#             a, b, c, d, e = settings
#
#             for order in orders:
#                 helper.send_tweet(order, a, b, c, d, e)
#         else:
#             pass
#
#         time.sleep(60)
#
# def reply():
#     # get the replies to its tweet, and reply to them
#     while True:
#         try:
#             replies = helper.get_replies()
#
#             for i, reply in enumerate(replies):
#                 curr_id,text, user = reply
#                 order, participants = helper.construct_conv_order(curr_id)
#                 helper.send_reply(order, participants,curr_id, user)
#                 if i==0:
#                     helper.record["reply"]["lastReplied_id"] = curr_id
#         except:
#             helper.record["reply"]["firstTime"] = True
#             print("Some error happened - reply")
#
#         time.sleep(15)
#
# def elon():
#     # get recent tweets of elonmusk, and reply to it
#     while True:
#         for celb in helper.celbs:
#             try:
#                 cleb_tweets = helper.get_celb_tweets(celb)
#                 for i, reply in enumerate(cleb_tweets):
#                     curr_id, text, user = reply
#                     order, participants = helper.construct_conv_order(curr_id)
#                     helper.send_reply(order, participants, curr_id, user)
#                     if i == 0:
#                         helper.record[celb]["lastReplied_id"] = curr_id
#             except:
#                 # this try and excpet block is to make program keep running even though some error happend
#                 helper.record[celb]["firstTime"] = True
#                 print("Some error happened - celb")
#
#         time.sleep(15)
#
# if __name__ == "__main__":
#     #print("testing whether the API keys is working well")
#     api.update_status("testing whether the API keys is working well")
#     # print("Start of the program\n\n")
#     # processes = []
#     # p1 = multiprocessing.Process(target=tweet)
#     # p1.start()
#     # processes.append(p1)
#     #
#     # p2=multiprocessing.Process(target=reply)
#     # p2.start()
#     # processes.append(p2)
#     #
#     # for process in processes:
#     #     process.join()
#

'''
consumer_key = "j7lAuTzbTjpCSwxOuW3cWt0SJ"
consumer_secret = "mYkiw2m1JrHf6SWNsLFgaIojcDSZ0JXFGu7CnxmTh0WGihO1XY"
oa_key = "1499630375756509184-ZVNGoEpRlBnpwOX9uI9xx589uAicpu"
oa_secret = "9xZDYpMDbFJBv6yYzoLpxU7onZGsjv3g034Xyj4l6qBqO"

https://twitter.com/oauth/request_token?oauth_consumer_key=j7lAuTzbTjpCSwxOuW3cWt0SJ&oauth_callback=oob

oauth_token=wSAL0gAAAAABZ6PiAAABgheeHaE&oauth_token_secret=3cdpn0NSHDTdWM04g4iivUFrmbgOmKQM&oauth_callback_confirmed=true

https://twitter.com/oauth/authenticate?oauth_token=wSAL0gAAAAABZ6PiAAABgheeHaE

3975488

https://twitter.com/oauth/access_token?oauth_token=wSAL0gAAAAABZ6PiAAABgheeHaE&oauth_verifier=3975488



`curl --request POST --url 'https://twitter.com/oauth/access_token?oauth_token=wSAL0gAAAAABZ6PiAAABgheeHaE&oauth_verifier=3975488'`


oauth_token=1499630375756509184-ZVNGoEpRlBnpwOX9uI9xx589uAicpu
&
oauth_token_secret=9xZDYpMDbFJBv6yYzoLpxU7onZGsjv3g034Xyj4l6qBqO
&user_id=1499630375756509184&screen_name=Justin_prg

'''