import random
import openai
from Resources import data
from Resources import keys
from newsapi import NewsApiClient
from datetime import date,timedelta, datetime
from Brain import  Brain

engine = "text-davinci-002"

class Creater:
    def send_tweet(self, order, a, b, c, d, e):
        # only used for creating contents - news!
        result = ""
        print(f"the order is:\n {order}")
        # get the response
        try:
            result = Brain().create_content(order)
            print(f"new tweet is {result}")
        except openai.error.OpenAIError as e:
            print(f"[send_tweet] openAI Error: {e}\n")


    def get_type(self):
        now = datetime.now().time().replace(second=0, microsecond=0)
        currH, currM = now.hour, now.minute
        curr = (currH, currM)
        if curr in data.news_times:
            return 'news'
        else:
            return None

    def create_order(self, type):
        if type == 'news':
            newsapi = NewsApiClient(api_key=keys.news_key)
            today = date.today()
            yesterday = today - timedelta(1)
            end = today.strftime("%Y-%m-%d")
            start = yesterday.strftime("%Y-%m-%d")
            new_things = []
            recent_news = newsapi.get_everything(
                domains='cnbc.com',
                from_param=start,
                to=end,
                language='en',
                sort_by='relevancy',
                page=1)

            str = recent_news['articles'][0]['title']
            if str.endswith('CNBC'):
                str = str[:-7]

            return [f"Friend:Feel free to express your emotion on: {str}\nYou:"], (0.5, 60, 1, 0.5, 0)





