import openai
from Resources import data
from Resources import keys
from newsapi import NewsApiClient
from datetime import date,timedelta, datetime
from Brain import  Brain
from Twitter import Twitter
import Settings

class Creater:
    def send_tweet(self, order):
        # creating content
        result = ""
        print(f"the order is:\n {order}")
        try:
            result = Brain().create_content(order)
            print(f"new tweet is {result}")
        except openai.error.OpenAIError as e:
            print(f"[send_tweet] openAI Error: {e}\n")

        # tweeting
        if Settings.production:
            Twitter().tweet_content(result)
        else:
            print("content tweeted - Development mode\n")

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

            return [f"Friend:Feel free to express your emotion on: {str}\nYou:"]



