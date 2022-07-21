import random
import openai
from Resources import data
from Resources import keys
from newsapi import NewsApiClient
from datetime import datetime
from Brain import Brain
from Twitter import Twitter
import Settings
import re

class Creater:
    def send_tweet(self, order):
        # creating content
        result = ""
        print(f"the order is:\n {order}")
        try:
            #create and process the string
            result = Brain().create_content(order)
            result = self.process_str(result)
            print(f"new tweet is {result}")
        except openai.error.OpenAIError as e:
            print(f"[send_tweet] openAI Error: {e}\n")

        # tweeting the content
        if Settings.production:
            Twitter().tweet_content(result)
        else:
            print("content tweeted - Development mode\n")

    def get_type(self):
        if Settings.production:
            now = datetime.now().time().replace(second=0, microsecond=0)
            currH, currM = now.hour, now.minute
            curr = (currH, currM)
            if curr in data.news_times:
                return 'news'
            else:
                return None
        else:
            return "news"

    def create_order(self, type):
        if type == 'news':
            newsapi = NewsApiClient(api_key=keys.news_key)
            recent_news = newsapi.get_top_headlines(
                category = random.choice(["science", "technology"]),
                language='en',
                page=1)

            str = recent_news['articles'][0]['title']
            print(str)
            return [f"{str}\n{Settings.prompt_create}\n:"]

    def process_str(self, result):
        result = re.sub('@[a-zA-Z_0-9]*', '', result)
        result = re.sub('#[a-zA-Z_0-9]*', '', result)

        return result

'''
categories = {"business", "entertainment", "general", "health", "science", "sports", "technology"}
'''