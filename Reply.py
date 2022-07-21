import openai
import tweepy as twitter
import re
from Resources import keys
from Twitter import Twitter
import Brain
import Settings

auth = twitter.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.oa_key, keys.oa_secret)
api = twitter.API(auth)

def send_reply(order,particpants,curr_id, user):
    result = ""
    # create a reply
    try:
        # create a response
        result = Brain.Brain().create_response(order, [f"{user}:", "You:"])
        # process the response
        result=process_str(result, particpants)
        print(f"My Reply: {result}")
    except openai.OpenAIError as e:
        print(f"[send_reply] openAI Error: {e}")

    # tweet the reply
    if Settings.production:
        try:
            Twitter().tweet_reply(result, curr_id)
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

def process_str(result, particpants):
    result = re.sub('@[a-zA-Z_0-9]*', '', result)
    taggins = ""
    for particpant in particpants:
        taggins += f'{particpant} '
    result = taggins + result
    result = re.sub('\n', '', result)

    last = result.find('Friend:')
    if last==-1:
        return result
    else:
        return result[:last]