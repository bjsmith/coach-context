
# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError
import telegram
from chat import ChatConfig, CBTIOInterface
from flask import Flask, request, jsonify
import requests
import os
import time
from session import SessionManager


WHERE WE'RE AT:

- GOING HALF-WAY THROUGH THE RECEIVING function
- JUST NEEDS SOME SMALL THINGS SET UP IN THERE
- THE MAIN ISSUE IS THAT I'M NOT SURE THE MESSSAGES ARE COMING THROUGH RELIABLY, AND THIS MAY BE A PROBLEM WITH THE WEBHOOK
- THE BLOODY WEBHOOK. PERHAPS I NEED TO USER ASYNC RATEHR THAN TRYING TO GET THIS TO WORK SYNCHRONOUSLY.
- ONE REASON I HAVEN'T IS BECAUSE THE BACKEND MIGHT NOT BE SET UP FOR ASYNC PROPERLY.


Possible routes through:

 - start from scratch, using requests and Flask
- start from scratch, using telegram for webhook, Flask, and still no async, but get the webhook right first.
 - start from scratch, using telegram and aysnc if neccessary

class TelegramConnectorApp:


    def __init__(self):
        self.app = Flask(__name__)
        self.telegram_url = 'https://api.telegram.org/bot' + ChatConfig.get_config()['telegrambottoken'] + '/'
        self.client = telegram.Bot(token=ChatConfig.get_config()['telegrambottoken'])
        
        self.register_routes()
        self.io = TelegramIO(self.send_message)
        self.session_manager = SessionManager(self.io)
        self.events_cache = []
        pass

    def run(self, *args, **kwargs):
        
        self.set_webhook()
        self.app.run(*args, **kwargs)

    def register_routes(self):
        token = ChatConfig.get_config()['telegrambottoken']
        #self.app.route("/", methods=['POST','GET'])(self.handle_events)
        # self.app.route("/")(self.hello)
        # # self.app.route("/url_verification")(self.slack_url_verify)
        # self.app.route("/events", methods=["POST"])(self.handle_events)
        self.app.route("/{}".format(token), methods=["POST"])(self.handle_events)
        self.app.route("/setwebhook", methods=["GET","POST"])(self.set_webhook)
        #self.app.route("/slack/events", methods=["POST"])(self.handle_event)

    #@app.route('/setwebhook', methods=['GET', 'POST'])
    def set_webhook(self):
        # we use the bot object to link the bot to our app which live
        # in the link provided by URL
        token = ChatConfig.get_config()['telegrambottoken']
        webhook_url = '{URL}{HOOK}'.format(
            URL=ChatConfig.get_config()['telegram_bot_url'],
            HOOK=token
        )
        
        url = self.telegram_url + 'setWebhook?url=' + webhook_url
        res = requests.get(url)
        return 'Webhook set'

    def send_message(self, channel_id, text):
        try:
            # Send a message using the Slack WebClient
            url = self.telegram_url + f'sendMessage?chat_id={channel_id}&text={message}'
            requests.get(url)
            #print(f"Message sent: {response['ts']} - {text}")
            print(f"Message sent: {text}")
        except Exception as e:
            # In case of errors, print the error message
            print(f"Error sending message: {e}")
        
    
    def handle_events(self):
        
        # if request.json['type']=='url_verification':
        #     return request.json['challenge']

        print("call to handle_events URL occured")
        payload = request.json
        event_id = payload['update_id']







        #track the events; if we already got this event, ignore
        #might want to just use update_id for this.
        self.events_cache = [event_id] + self.events_cache[:99999]
        if event_id in self.events_cache[1:]:
            print('ignoring duplicate event')
            return jsonify({'status': 'ok'})
        
        #get current unix timestamp
        current_ts = int(time.time())

        if 'message' in payload:

            #this is a message from a user
            message = payload['message']

            if message['from']['is_bot']:
                print('bot message')
                return jsonify({'status': 'ok'})


            text = message['text']
            user_id = message['from']['id']

            channel_id = user_id # this is different in slack, but just using the username here.
            ts = message['date']
            print("receiving message from user " + str(user_id) + " (" + str(ts) + "): " + text)

            #temporary measure to avoid processing bounced events
            #this can occur during debugging.
            if ts<float(current_ts-30):
                print('ignoring old event')
                return jsonify({'status': 'ok'})


            # user_id = event.get("user_id")
            # message = event.get("message")
            self.session_manager.handle_incoming_message(channel_id, user_id, text, ts=ts)
            #self.send_response_to_slack(response)

            
            #self.send_message(channel_id, f"Received your direct message: {text}")
            print(' received a message from a user ({user_id}) {text}')
            #self.send_message(channel_id, f"response")


        return jsonify({'status': 'ok'})


class TelegramIO(CBTIOInterface):
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
    my_flask_app =TelegramConnectorApp()
    my_flask_app.run(debug=True, port=3001)
    
