# Justin_prg

This is a twitter bot that acts like a perosnal account

## Features

- **creating contents**

Every 10PM it get recent one news from cnbc.com using news api. Then tweet about it


- **replying to its on tweet**

Every 15 seconds, it check whetehr it got a reply tweet to its on tweet. If yes it reply to its tweet

- **replying to elons tweet**

Every 15 seconds, it check whether Elon Musk tweeted a tweet.(Only nature tweet, not reply to others tweet). Due to some enginerring limitation, it can reply to Elon's reply tweet only when you first started running this program



### Things need to consider




Theortically elon() func and reply() func can get collided. But odds is very low


elon() function get all tweets for a given celb and reply() get all tweets that mentioned me
If the certain celb reply to you, then collide will happen. But as now it is very unlikely to happen.
So We decided not to put any more resource on it as now.

Other erros

Tweet network error - not my fault
JSON error - commented json file updating coded

deleted tweet - if error happens in elon() or reply() func, in except block it resets firstTime to be True

** This will make the program to continue running even after facing erros while executing elon() or reply().

But I'm worried that this might cause the bot to reply to certain tweet recursively.

again but, I guess this won't happen
**
