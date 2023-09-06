#this is a minimal example script to get a reliable telegram connector working
from chat import ChatConfig
telegram_token = ChatConfig.get_config()['telegrambottoken']

#https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---Your-first-Bot

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.ext import MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="echo: " + update.message.text)

if __name__ == '__main__':
    application = ApplicationBuilder().token(telegram_token).build()
    
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    
    application.run_polling()