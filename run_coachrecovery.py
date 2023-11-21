from telegram_connector_app import TelegramConnectorApp
from chat import ChatConfig
config = ChatConfig.get_config()
telegram_code = config['coachrecovery_bot']

print("start of chat config:")

print(config['telegram_admin_ids'])
print(len(config['telegram_admin_ids']))

tca = TelegramConnectorApp(telegram_code)
print("starting up connector app...")
tca.run()

print("running telegram connector app")