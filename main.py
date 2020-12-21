from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
import urllib3
import os
import json
import datetime
from os import walk
import random
import ast
from json import dumps, loads, JSONEncoder, JSONDecoder
import pickle

import constants

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

http = urllib3.PoolManager()

mypath = './images'
f = []
for (dirpath, dirnames, filenames) in walk(mypath):
    f.extend(filenames)
    break

job_minute = None

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Store chat ids
persistent_data = {'chat_ids': [], "image_index": 0}

if os.path.isfile('data.txt'):
    with open('data.txt', 'r') as file:
        persistent_data = json.load(file)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def start(update, context):
    """Send a message when the command /start is issued."""
    chat_id = update.effective_chat.id
    if not chat_id in persistent_data['chat_ids']:
        persistent_data['chat_ids'].append(chat_id)

        with open('data.txt', 'w') as file:
            json.dump(persistent_data, file)

        if not job_minute.enabled:
            job_minute.enabled = True

        context.bot.send_message(chat_id=chat_id,
                                text="Toad delivery has been enabled for your chat!")
    else:
        context.bot.send_message(chat_id=chat_id,
                                text="Toads already know about this place")


def stop(update, context):
    """Send a message when the command /start is issued."""
    chat_id = update.effective_chat.id
    if chat_id in persistent_data['chat_ids']:
        persistent_data['chat_ids'] = list(filter(
            lambda id: id != chat_id, persistent_data['chat_ids']))
        with open('data.txt', 'w') as file:
            json.dump(persistent_data, file)
        context.bot.send_message(chat_id=chat_id,
                                text="Toads will no longer visit you :c")
    else:
        context.bot.send_message(chat_id=chat_id,
                                text="Toads already left")


def help(update, context):
    """Send a message when the command /help is issued."""
    helpText = '''/stop - unsubscribe from the toad goodness. Not recommended'''
    update.message.reply_text(helpText)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def send_toad(context: CallbackContext):
    global job_minute
    global persistent_data

    if len(persistent_data['chat_ids']) == 0:
        job_minute.enabled = False
        return

    if persistent_data['image_index'] >= len(f):
        persistent_data['image_index'] = 0

    filename = f[persistent_data['image_index']]
    persistent_data['image_index'] += 1

    with open('data.txt', 'w') as file:
        json.dump(persistent_data, file)

    with open('./images/' + filename, 'rb') as file_image:
        for id in persistent_data['chat_ids']:
            context.bot.send_photo(chat_id=id,
                                   photo=file_image,
                                   caption='Nice')
            file_image.seek(0)


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
    global job_minute
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
