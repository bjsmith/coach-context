
import asyncio
import threading
from flask import Flask
import time
from concurrent.futures import ProcessPoolExecutor

from telegram_connector_app import TelegramConnectorApp
from chat import ChatConfig
config = ChatConfig.get_config()
telegram_code = config['coachrecovery_bot']

print("start of chat config:")

# print(config['telegram_admin_ids'])
# print(len(config['telegram_admin_ids']))




def async_operation(x):
    tca = TelegramConnectorApp(telegram_code)
    print("starting up connector app...")
    tca.run()


from web_app import *
# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello, World!'

# def flask_app():
#     app.run(port=5000)

def run_web_app(port=5001):
    try:
        wapp.run(port=port)
        if port>5100:
            raise Exception("port too high")
    except OSError:
        run_web_app(port + 1)

async def start_async_op():
    p = ProcessPoolExecutor(2)
    await loop.run_in_executor(p, async_operation, 5)

# Create a separate thread for flask app    
t = threading.Thread(target=run_web_app)
t.start()

loop = asyncio.get_event_loop()
loop.run_until_complete(start_async_op())


# raise NotImplementedError("you can't use threading.thread with telegram because it's async. try a different way.")
# from telegram_connector_app import TelegramConnectorApp
# from chat import ChatConfigx
# from threading import Thread

# def run_coach_recovery():
#     telegram_code = ChatConfig.get_config()['coachrecovery_bot']

#     tca = TelegramConnectorApp(telegram_code)
#     print("starting up connector app...")
#     tca.run()

# def run_coach_context():
#     tca = TelegramConnectorApp()
#     tca.run()
    
# Thread(target=run_coach_recovery).start()
# Thread(target=run_coach_context).start()