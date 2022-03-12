import random
import openai
import data
from newsapi import NewsApiClient
import keys
from datetime import date,timedelta


def dev_order(tag):
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

def get_random_word():
    response = openai.Completion.create(
  engine="text-davinci-001",
  prompt="Give me a random noun word",
  temperature=0.66,
  max_tokens=64,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

    return response

def create_order(type):
    if type == 'dev':
        root = random.choice(list(data.tags.items()))
        selected_tag = random.choice(list(root[1]))
        return [dev_order(selected_tag)], (0.15,64,1,0,0)
    if type == "joke":
        topic= get_random_word()
        return [f"Make a joke about {topic} that gives punchline or make people view it in other view"], (0.5,150,1,0,0)
    if type=='news':
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

        for i in range(len(recent_news)):
            str=recent_news['articles'][i]['title']
            if str.endswith('CNBC'):
                str=str[:-7]

            str=f"Feel free to express your emotion on: {str}"
            new_things.append(str)

        return new_things, (0,150,1,0,0)