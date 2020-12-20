from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
import urllib3
import os
import json
import datetime
from os import walk
import random

import constants

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

http = urllib3.PoolManager()

mypath = './images'
f = []
for (dirpath, dirnames, filenames) in walk(mypath):
    f.extend(filenames)
    break
image_index = 0

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Store chat ids
chat_ids = set()

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def start(update, context):
    """Send a message when the command /start is issued."""
    chat_id = update.effective_chat.id
    chat_ids.add(chat_id)
    context.bot.send_message(chat_id=chat_id,
                             text="Toad delivery has been enabled for your chat!")


def stop(update, context):
    """Send a message when the command /start is issued."""
    chat_id = update.effective_chat.id
    chat_ids.remove(chat_id)
    context.bot.send_message(chat_id=chat_id,
                             text="Toads will no longer visit you :c")


def help(update, context):
    """Send a message when the command /help is issued."""
    helpText = '''/stop - unsubscribe from the toad goodness. Not recommended'''
    update.message.reply_text(helpText)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def send_toad(context: CallbackContext):
    global image_index
    if image_index >= len(f):
        image_index = 0

    filename = f[image_index]
    image_index += 1
    image = open('./images/' + filename, 'rb')
    for id in chat_ids:
        context.bot.send_photo(chat_id=id,
                               photo=image,
                               caption='Nice')


def getArgument(text):
    # trim command itself
    arg = text[4:len(text)].strip()

    # trim name of the bot in the end, if called with it
    if (len(arg) >= 15):
        arg = arg[0:len(arg) - 15]

    return arg


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    token = os.getenv("BOT_TOKEN")

    print(token)

    updater = Updater(token=token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("help", help))

    jq = updater.job_queue
    job_minute = jq.run_repeating(send_toad, interval=15, first=0)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
