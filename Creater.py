import random
import openai
import data
import keys
from newsapi import NewsApiClient
from datetime import date,timedelta, datetime

engine = "text-davinci-002"

class Creater:

    def send_tweet(self, order, a, b, c, d, e):
        # only used for creating contents - news!
        result = ""
        count = 0
        print(f"the order is:\n {order}")

        # get the response
        try:
            while True:
                response = openai.Completion.create(
                    engine=engine,
                    prompt=order,
                    temperature=a,
                    max_tokens=b,
                    top_p=c,
                    frequency_penalty=d,
                    presence_penalty=e,
                    stop=["Friend:"]
                )

                count += 1
                result += response['choices'][0]['text']
                order += response['choices'][0]['text']
                if count == 3 or response['choices'][0]['text'] == '':
                    break

            print(f"new tweet is {result}")
        except openai.error.OpenAIError as e:
            print(f"[send_tweet] openAI Error: {e}\n")


    def get_type(self):
        now = datetime.now().time().replace(second=0, microsecond=0)
        currH, currM = now.hour, now.minute
        curr = (currH, currM)
        if curr in data.dev_times:
            return 'dev'
        elif curr in data.joke_times:
            return 'joke'
        elif curr in data.news_times:
            return 'news'
        else:
            return None

    def get_random_word(self):

        response = openai.Completion.create(
            engine=engine,
            prompt="Give me a random noun word",
            temperature=0.66,
            max_tokens=64,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return response

    def dev_order(self, tag):
        choices = [
            f"Give me your personal thought about {tag}?",
            f"Say as if you used {tag} for the first time",
            f"Say as if you really like {tag}",
            f" Say something negative thing about {tag} and one or more way to solve problem.",
            f"Say about {tag} as if you mastered it",
            f"Say as if you’re learning {tag} and going through some hardship"
            f"Ask a stupid question related to {tag}"
            f"Say anything related to {tag}"
            f"Any recent news on {tag}?"
        ]

        return random.choice(choices)

    def create_order(self, typr):
        if type == 'dev':
            root = random.choice(list(data.tags.items()))
            selected_tag = random.choice(list(root[1]))
            return [self.dev_order(selected_tag)], (0.15, 64, 1, 0, 0)
        if type == "joke":
            topic = self.get_random_word()
            return [f"Make a joke about {topic} that gives punchline or make people view it in other view"], (
            0.5, 150, 1, 0, 0)
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




'''


'''