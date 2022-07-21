import tweepy as twitter
from Resources import keys

auth = twitter.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.oa_key, keys.oa_secret)
api = twitter.API(auth)

record = {
    "reply": {"firstTime": True, "lastReplied_id": 0},
    "elonmusk": {"firstTime": True, "lastReplied_id": 0},
    "engineers_feed": {"firstTime": True, "lastReplied_id": 0},
    "tim_cook": {"firstTime": True, "lastReplied_id": 0},
    "lexfridman": {"firstTime": True, "lastReplied_id": 0}
}

class Twitter:
    def get_replies(self):
        replies = []
        if record["reply"]["firstTime"]:
            # len(rd) should be 1 all the time,no matter wgat, but due to some error of Twitter API which say there was any no recent tweet, added While True block
            # from the second time it is OK for such error happening. Because at first time it have to update recent id. Which will be used in second time
            try:
                rd = api.mentions_timeline(count=1)
                print(f"reply-first Time: {len(rd)}")
                for dot in rd:
                    replies.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))
                record["reply"]["firstTime"] = False
            except twitter.errors.TweepyException as e:
                print(f"[get_replies] (First time) Twitter Error: {e}\n")
        else:
            try:
                rd = api.mentions_timeline(since_id=record["reply"]["lastReplied_id"])
                if (len(rd) > 0):
                    print(f"reply-second Time: {len(rd)}")
                for dot in rd:
                    replies.append((dot._json['id'], dot._json['text'], dot._json['user']['screen_name']))
            except twitter.errors.TweepyException as e:
                print(f"[get_replies] (Second time) Twitter Error: {e}\n")
        return replies


    def tweet_reply(self, result, curr_id):
        if len(result) > 280:
            split_strings = []
            for index in range(0, len(result), 270):
                split_strings.append(result[index: index + 270])

            for i, sub_str in enumerate(split_strings):
                if i == 0:
                    api.update_status(status=sub_str, in_reply_to_status_id=curr_id)

                else:
                    result = api.user_timeline(user_id='justin_prg', count=1)
                    recent_id = result[0]._json['id']
                    api.update_status(status=sub_str, in_reply_to_status_id=recent_id)

        # if result is shorter than 280 characters
        else:
            api.update_status(status=result, in_reply_to_status_id=curr_id)
            print("reply-tweeted! \n")

    def tweet_content(self, result):
        if len(result) > 280:
            split_strings = []
            for index in range(0, len(result), 270):
                split_strings.append(result[index: index + 270])

            for i, sub_str in enumerate(split_strings):
                if i == 0:
                    api.update_status(sub_str)
                else:
                    result = api.user_timeline(user_id='justin_prg', count=1)
                    recent_id = result[0]._json['id']
                    api.update_status(status=sub_str, in_reply_to_status_id=recent_id)

        # if result is shorter than 280 characters
        else:
            api.update_status(result)
            print("content-tweeted! \n")