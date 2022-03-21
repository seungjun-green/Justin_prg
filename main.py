import time
import keys
import openai
import tweepy as twitter
import helper
import time
from git import Repo
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


# if __name__ == "__main__":
#     processes = []
#     p1 = multiprocessing.Process(target=tweet)
#     p1.start()
#     processes.append(p1)
#
#     p2=multiprocessing.Process(target=reply)
#     p2.start()
#     processes.append(p2)
#
#     for process in processes:
#         process.join()





PATH_OF_GIT_REPO = r'path\to\your\project\folder\.git'  # make sure .git folder is properly configured
COMMIT_MESSAGE = 'comment from python script'

def git_push():
    try:
        repo = Repo(PATH_OF_GIT_REPO)
        repo.git.add(update=True)
        repo.index.commit(COMMIT_MESSAGE)
        origin = repo.remote(name='origin')
        origin.push()
    except:
        print('Some error occured while pushing the code')

git_push()




