from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from chat import CBTTerminal, ChatConfig
from flask import Flask, request, jsonify
import os

from slack_bolt import App
# from slack_bolt.adapter.socket_mode import SocketModeHandler

# # Install the Slack app and get xoxb- token in advance
# app = App(token=os.environ["SLACK_BOT_TOKEN"])

# if __name__ == "__main__":
#     SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

class CBTSlackChat(CBTTerminal):
    """
    manages input and output with the client on slack.
    """
    # keep this as simple as possible; just input and output
    def __init__(self):
        #self.app = Flask(__name__)
        config = ChatConfig.get_config()
        self.app = App(
            token=config['slackbottoken'],
            signing_secret=config['slacksigningsecret']
        )

        #os.system('clear')
        self.register_routes()
        pass

    def run(self, *args, **kwargs):
        #self.client = WebClient(token=)
        #self.app.run(*args, **kwargs)
        self.app.start(*args, **kwargs)

    def register_routes(self):
        #self.app.event("app_mention")(self.hello)
        self.app.message("hello")(self.hello)
        self.app.message("/")(self.greet)
        # self.app.command("/")(self.greet)
        # self.app.command("/hello")(self.hello)
        
        # self.app.add_handler("/", methods=['POST','GET'])(self.base)
        # self.app.route("/hello")(self.hello)
        # self.app.route("/url_verification")(self.slack_url_verify)
        # self.app.route("/events", methods=["POST"])(self.handle_events)
        # #self.app.route("/slack/events", methods=["POST"])(self.handle_event)
    

    def base(self):
        if request.method=='POST':
            print(request)
        
        print("call to base URL occured")
        print(request)
        return ("Hello at the base URL")
    
    def greet(self):
        print("user called the base")
        return("Hello from the base command")
    
    def slack_url_verify(self):
        print("call to slack_url_verify URL occured")
        print(request.json)
        return request.json['challenge']

    def hello(self, message, say):
        print("hello was called.")
        # say() sends a message to the channel where the event was triggered
        say(
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click Me"},
                        "action_id": "button_click"
                    }
                }
            ],
            text=f"Hey there <@{message['user']}>!"
        )


    def print_output(self, output_text):
        print("\nTherapist: \n" + output_text + "\n\n")

    def get_input(self, prompt_text=None):
        if prompt_text is not None:
            print(prompt_text)
        return input("You: \n")
    

    def send_message(self, channel_id, text):
        try:
            # Send a message using the Slack WebClient
            response = self.client.chat_postMessage(
                channel=channel_id,
                text=text
            )
            print(f"Message sent: {response['ts']} - {text}")
        except SlackApiError as e:
            # In case of errors, print the error message
            print(f"Error sending message: {e}")
        
    
    def handle_events(self):
        print("call to handle_events URL occured")
        payload = request.json
        event = payload.get('event', {})

        if event.get('type') == 'app_mention':
            text = event.get('text', '')
            channel_id = event.get('channel')
            #send_message(channel_id, f"Received your message: {text}")
        elif event.get('type') == 'message' and event.get('channel_type') == 'im':
            text = event.get('text', '')
            channel_id = event.get('channel')
            self.send_message(channel_id, f"Received your direct message: {text}")

        return jsonify({'status': 'ok'})
        

if __name__ == '__main__':
    #my_flask_app = CBTSlackChat()
    my_bolt_app = CBTSlackChat()
    my_bolt_app.run(port=int(os.environ.get("PORT", 3000)))
    #my_flask_app.run(debug=True, port=int(os.environ.get("PORT", 3000)))
    

