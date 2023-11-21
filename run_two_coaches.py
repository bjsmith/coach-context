
raise NotImplementedError("you can't use threading.thread with telegram because it's async. try a different way.")
from telegram_connector_app import TelegramConnectorApp
from chat import ChatConfig
from threading import Thread

def run_coach_recovery():
    telegram_code = ChatConfig.get_config()['coachrecovery_bot']

    tca = TelegramConnectorApp(telegram_code)
    print("starting up connector app...")
    tca.run()

def run_coach_context():
    tca = TelegramConnectorApp()
    tca.run()
    
Thread(target=run_coach_recovery).start()
Thread(target=run_coach_context).start()