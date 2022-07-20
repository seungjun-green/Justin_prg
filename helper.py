import openai
import tweepy as twitter
import re
from Resources import keys
import Twitter

production = False
engine = "text-davinci-002"

auth = twitter.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.oa_key, keys.oa_secret)
api = twitter.API(auth)


def create_stop_seq(user):
    return [f"{user}:", "You:"]

def send_reply(order,particpants,curr_id, user):
    result = ""
    count = 0
    stop = create_stop_seq(user)
    # get the response
    try:
        while True:
            response = openai.Completion.create(
                engine=engine,
                prompt=order,
                temperature=0.5,
                max_tokens=60,
                top_p=1,
                frequency_penalty=0.5,
                presence_penalty=0,
                stop=stop
            )

            count += 1
            result += response['choices'][0]['text']
            order += response['choices'][0]['text']
            if count == 3 or response['choices'][0]['text'] == '':
                break

        # tweet the result
        result = re.sub('@[a-zA-Z_0-9]*', '', result)
        taggins = ""
        for particpant in particpants:
            taggins+=f'{particpant} '



        result = taggins + result
        result = re.sub('\n', '', result)
        result=process_str(result)
        print(f"My Reply: {result}")
    except openai.OpenAIError as e:
        print(f"[send_reply] openAI Error: {e}")

    # tweet the reply
    if production:
        try:
            Twitter.Twitter().tweet(result, curr_id)
        except twitter.errors.TweepyException as e:
            print(f"[send_reply] Twitter Error: {e}\n")
    else:
        print("reply tweeted - Development mode\n")


def construct_conv_order(tw_id):
    chats = []
    particpants = set()
    rd = api.get_status(id=tw_id)
    while True:
        try:
            data = rd[0]._json
        except:
            data = rd._json

        text = data['text']
        #text = re.sub('@[a-zA-Z_0-9]*', '', text)
        user = data['user']['screen_name']
        if user == 'Justin_prg':
            user = 'You'
        else:
            particpants.add(f'@{user}')

        chats.append(f"{user}:{text}")
        parent_id = data['in_reply_to_status_id']
        if parent_id is None:
            break

        rd = api.get_status(id=parent_id)
    # reverse chats
    chats.reverse()
    order = ""
    for chat in chats:
        chat = re.sub('\n', '', chat)
        chat += '\n'
        order += chat

    order+='You:'
    print("\n-------start of the order-------")
    print(order)
    print("-------end of the order-------\n")
    return order, particpants

def process_str(str):
    last = str.find('Friend:')
    if last==-1:
        return str
    else:
        return str[:last]
