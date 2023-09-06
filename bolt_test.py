from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from chat import CBTTerminal, ChatConfig
from flask import Flask, request, jsonify
import os

from slack_bolt import App
# from slack_bolt.adapter.socket_mode import SocketModeHandler

config = ChatConfig.get_config()

app = App(
            token=config['slackbottoken'],
            signing_secret=config['slacksigningsecret']
        )

# Listens to incoming messages that contain "hello"
# To learn available listener arguments,
# visit https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")

@app.message("/")
def message_hello(message, say):
    return("ello")


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))