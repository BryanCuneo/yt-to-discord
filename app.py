""" 
yt-to-discord - YouTube push notifications to Discord webhooks
Copyright (C) 2021  Bryan Cuneo

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import xmltodict
import yaml

from discord_webhook import DiscordWebhook
from flask import Flask, request
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
        # YT will send a challenge from time to time to confirm the server is alive.
        return challenge

    try:
        # Parse the XML from the POST request into a dict.
        xml_dict = xmltodict.parse(request.data)

        # Lazy verification - check if the POST request is from a channel ID that's been
        # set in config["channel_ids"].  Skip the check if that config option is empty.
        channel_id = xml_dict["feed"]["entry"]["yt:channelId"]
        if config["channel_ids"] != [] and channel_id not in config["channel_ids"]:
            return "", 403

        # Parse out the video URL.
        video_url = xml_dict["feed"]["entry"]["link"]["@href"]
        print("New video URL: {}".format(video_url))

        # Send the message to the webhook URL.
        # https://discord.com/developers/docs/resources/webhook
        message = config["message_prefix"] + "\n" + video_url
        webhook = DiscordWebhook(url=config["webhook_url"], content=message)
        response = webhook.execute()

    except (ExpatError, LookupError):
        # request.data contains malformed XML or no XML at all, return FORBIDDEN.
        return "", 403

    # Everything is good, return NO CONTENT.
    return "", 204


if __name__ == "__main__":
    app.run()
