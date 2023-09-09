
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from chat import ChatConfig, CoachingIOInterface
from flask import Flask, request, jsonify
import os
import time
from session import SessionManager


class SlackConnectorApp:


    def __init__(self):
        self.app = Flask(__name__)
        #os.system('clear')
        self.register_routes()
        self.io = SlackIO(self.send_message)
        self.session_manager = SessionManager(self.io)
        self.events_cache = []
        pass

    def run(self, *args, **kwargs):
        self.client = WebClient(token=ChatConfig.get_config()['slackbottoken'])
        self.app.run(*args, **kwargs)

    def register_routes(self):
        #self.app.route("/", methods=['POST','GET'])(self.handle_events)
        self.app.route("/")(self.hello)
        # self.app.route("/url_verification")(self.slack_url_verify)
        self.app.route("/events", methods=["POST"])(self.handle_events)
        #self.app.route("/slack/events", methods=["POST"])(self.handle_event)

    def hello(self):
        return("Hello World")

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
        
        if request.json['type']=='url_verification':
            return request.json['challenge']

        print("call to handle_events URL occured")
        payload = request.json
        event = payload.get('event', {})




        if 'bot_id' in event:
            print('bot message')
            return jsonify({'status': 'ok'})


        #track the events; if we already got this event, ignore
        self.events_cache = [event] + self.events_cache[:99999]
        if event in self.events_cache[1:]:
            print('ignoring duplicate event')
            return jsonify({'status': 'ok'})
        
        #get current unix timestamp
        current_ts = int(time.time())



        if event.get('type') == 'app_mention':
            text = event.get('text', '')
            channel_id = event.get('channel')
            #send_message(channel_id, f"Received your message: {text}")
        elif event.get('type') == 'message' and event.get('channel_type') == 'im':
            text = event.get('text', '')
            user_id = event.get('user', '')
            channel_id = event.get('channel')
            ts = event['ts']
            print("receiving message from user " + str(user_id) + " (" + ts + "): " + text)

            #temporary measure to avoid processing bounced events
            #this can occur during debugging.
            if event.get('ts'):
                if float(event['ts'])<float(current_ts-30):
                    print('ignoring old event')
                    return jsonify({'status': 'ok'})


            # user_id = event.get("user_id")
            # message = event.get("message")
            self.session_manager.handle_incoming_message(channel_id, user_id, text, ts=event['ts'])
            #self.send_response_to_slack(response)

            
            #self.send_message(channel_id, f"Received your direct message: {text}")
            print(' received a message from a user ({user_id}) {text}')
            #self.send_message(channel_id, f"response")


        return jsonify({'status': 'ok'})


class SlackIO(CoachingIOInterface):
    """
    creates a mode-agnostic pattern for the therapist to use to communicate with the client
    """
    def __init__(self, send_message_callback):
        self.send_message_callback = send_message_callback
        pass

    def send_message(self, message, channel_id):
        self.send_message_callback(channel_id, message)

    def indicate_response_coming(self):
        pass

if __name__ == '__main__':
    my_flask_app = SlackConnectorApp()
    my_flask_app.run(debug=True, port=3001)
    
