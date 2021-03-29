# yt-to-discord
Utilize Discord's webhooks to receive new video notifications via YouTube's PubSubHubbub push notifications.

# How It Works
YouTube offers push notifications in the form of a [PubSubHubbub server-to-server interface](https://pubsubhubbub.appspot.com/subscribe), though the [documentation](https://developers.google.com/youtube/v3/guides/push_notifications) is fairly lacking. This small Flask server implements the required callback URL on the `/feed` route and parses out the URL for the video in the notification. An unfortunate limitation is that a push notification is sent out for both a new video upload and an edit to the description/title of an existing video. The XML content seems to be the same for each type of notification, so there's no easy way to differentiate.

The other half of the equation is [Discord's webhooks](https://discord.com/developers/docs/resources/webhook). Once this server receives a push notification from YouTube and parses out the video URL, a message containing that URL is sent to a webhook to be posted in the associated Discord text channel.

# How to Use
### Step One - The Normal Stuff:
[Clone](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) the repo, [make a virtual environment](https://www.askpython.com/python/examples/virtual-environments-in-python#2-creating-virtual-environments), and install the dependencies. Ex:
```
git clone https://github.com/BryanCuneo/yt-to-discord.git
cd yt-to-discord
python3 -m venv venv
pip install -r .\requirements.txt
```

### Step Two - Update config.yaml:
`webhook_url`: Once you create a webhook (see the 'Making a Webhook' section [here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)), you'll see a button labeled 'Copy Webhook URL.'

![Picture of the 'Copy Webhook URL' button](https://i.imgur.com/O1zrDJ3.png)

Click that and paste the resulting link here in `config.yaml`.

`message_prefix`: A string to be included in the message with the video URL.

### Step Three - Serve the Server
For easy testing purposes, you can run the Flask dev server on your local machine then expose it to the web with something like [ngrok](https://ngrok.com/download). Ex:
```
flask run --host=0.0.0.0
```
Then in another terminal:
```
ngrok http 5000
```
You'll get something like the following. Copy the first forwarding URL for step four.

![ngrok startup](https://i.imgur.com/JFLXTP7.png)

### Step Four - Subscribe
Navigate to the [Google PubSubHubbub subscription page](https://pubsubhubbub.appspot.com/subscribe):

![YouTube push notification subscription interface](https://i.imgur.com/TWzvDZ8.png)

In the 'Subscribe/Unsibscribe' mode, fill out the first four boxes:
 * Callback URL - the URL you copied in step 3, followed by /feed. Ex: `http://1829c24236ed.ngrok.io/feed`
 * Topic URL - `https://www.youtube.com/xml/feeds/videos.xml?channel_id=CHANNEL_ID` where CHANNEL_ID is the YouTube channel ID for the channel you'd like to subscribe to.
 * Verify type  - `Asynchronous`
 * Mode - `Subscribe`
Press the 'Do It!' button. Within a few minutes, you should see a GET request to /feed on your ngrok interface and a response code of 200.

![ngrok subscription confirmation request](https://i.imgur.com/q557OZf.png)

### Step Five - Waiting and Beyond
From here, you'll have to wait until there is activity on the channel you subscribed to. For testing purposes you can simply subscribe to your own personal YouTube channel and upload a short video. You can then edit the description repeatedly every time you wish to generate a new notification. Each notification should show up as a POST to /feed with a response code of 204.

![ngrok push notification received](https://i.imgur.com/YbsMY9f.png)

Once you're satisfied with the functionality you'll want a proper hosting solution rather than Flask's dev server. There are infinite possibilities here including some [free options](https://wiki.python.org/moin/FreeHosts).
