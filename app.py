import xmltodict
import yaml

from discord_webhook import DiscordWebhook
from flask import Flask
from flask import request
from xml.parsers.expat import ExpatError


try:
    with open("./config.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
except FileNotFoundError:
    print("Unable to load config file: 'config.yaml'")
    print("Exiting...")
    exit(1)


app = Flask(__name__)


@app.route("/feed", methods=["GET", "POST"])
def feed():
    """Accept and parse requests from YT's pubsubhubbub.
    https://developers.google.com/youtube/v3/guides/push_notifications
    """

    challenge = request.args.get("hub.challenge")
    if challenge:
        # YT will send a challenge from time to time to confirm the server is alive
        return challenge

    try:
        # Parse the XML from the POST request
        feed_xml = xmltodict.parse(request.data)

        video_url = feed_xml["feed"]["entry"]["link"]["@href"]
        print("New video URL: {}".format(video_url))

        # Send the message to the webhook URL.
        message = config["message_prefix"] + "\n" + video_url
        webhook = DiscordWebhook(url=config["webhook_url"], content=message)
        response = webhook.execute()

    except (ExpatError, LookupError):
        # request.data contains malformed XML or no XML at all, return FORBIDDEN
        return "", 403

    # Everything is good, return NO CONTENT
    return "", 204


if __name__ == "__main__":
    app.run()
