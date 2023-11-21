
# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError
import telegram
from chat import ChatConfig, CoachingIOInterface
from flask import Flask, request, jsonify
import requests
import os
import time
from session import AsyncSessionManager

# import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.ext import MessageHandler, filters

# OK SO this is not going to work
# because we've designed it asynchronusly
# it's not compatible with running SessionManager
# which is designed to be synchronous
# we'd have to rewrite SessionManager to be async
# I don't know how to do that
# possibly we can use the deliver_cbt, but we can't use the SessionManager as it is.


class TelegramConnectorApp:


    def __init__(self, telegram_token=None):
        # logging.basicConfig(
        # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        # level=logging.INFO
        # )
        
        if telegram_token is None:
            telegram_token = ChatConfig.get_config()['telegrambottoken']
        application = ApplicationBuilder().token(telegram_token).build()
        # self.client = telegram.Bot(token=ChatConfig.get_config()['telegrambottoken'])

        #start_handler = CommandHandler('start', self.start)
        

        #application.add_handler(start_handler)
        

        self.app = application

        
        self.register_handlers()
        self.io = TelegramIO(self.send_message)
        self.session_manager = AsyncSessionManager(self.io)
        self.events_cache = []
        pass

    def run(self, *args, **kwargs):
        self.app.run_polling()
        # self.set_webhook()
        # self.app.run(*args, **kwargs)

    def register_handlers(self):
        msg_received_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_msg)
        self.app.add_handler(msg_received_handler)
        

    async def send_message(self, channel_id, text):
        try:
            # Send a message using the Slack WebClient
            #context.bot.send_message(chat_id=update.effective_chat.id, text="alt-echo: " + update.message.text)
            #print(f"Message sent: {response['ts']} - {text}")
            await self.app.bot.send_message(chat_id=channel_id, text=text)
            print(f"Message sent: {text}")
        except Exception as e:
            # In case of errors, print the error message
            print(f"Error sending message: {e}")
        
    
    async def handle_msg(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        #self.app.bot.send_message(chat_id=user_id, text="hello world")

        print("call to handle_events URL occured")
        # payload = request.json
        # event_id = payload['update_id']




            # #this is a message from a user
            # message = payload['message']

            # if message['from']['is_bot']:
            #     print('bot message')
            #     return jsonify({'status': 'ok'})

        #message = {}
        #current_ts =0
        text = message['text']
        user_id = update.effective_user.id

        channel_id = user_id # this is different in slack, but just using the username here.
        ts = message['date'].timestamp()
        print("receiving message from user " + str(user_id) + " (" + str(ts) + "): " + text)

        #temporary measure to avoid processing bounced events
        #this can occur during debugging.
        # if ts<float(current_ts-30):
        #     print('ignoring old event')
        #     return jsonify({'status': 'ok'})


        # user_id = event.get("user_id")
        # message = event.get("message")
        await self.session_manager.handle_incoming_message(channel_id, user_id, text, ts=ts)
        #self.send_response_to_slack(response)

        
        #self.send_message(channel_id, f"Received your direct message: {text}")
        print(' received a message from a user ({user_id}) {text}')
        #self.send_message(channel_id, f"response")


        #return jsonify({'status': 'ok'})


class TelegramIO(CoachingIOInterface):
    """
    creates a mode-agnostic pattern for the therapist to use to communicate with the client
    """
    def __init__(self, send_message_callback):
        self.send_message_callback = send_message_callback
        pass

    async def send_message(self, message, channel_id):
        await self.send_message_callback(channel_id, message)

    def indicate_response_coming(self):
        pass

if __name__ == '__main__':
    # my_flask_app =TelegramConnectorApp()
    # my_flask_app.run(debug=True, port=3001)
    tca = TelegramConnectorApp()
    tca.run()
    
