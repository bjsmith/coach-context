from telegram_connector_app import TelegramConnectorApp
from chat import ChatConfig
telegram_code = ChatConfig.get_config()['coachrecovery_bot']

tca = TelegramConnectorApp(telegram_code)
tca.run()