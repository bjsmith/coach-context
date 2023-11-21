from telegram_connector_app import TelegramConnectorApp
from chat import ChatConfig
telegram_code = ChatConfig.get_config()['coachrecovery_bot']

tca = TelegramConnectorApp(telegram_code)
print("starting up connector app...")
tca.run()

print("running telegram connector app")