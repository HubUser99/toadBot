from telegram.ext import Updater, CommandHandler, CallbackContext, Job
import logging
import os
import json
from utils.files import get_data_from_file, save_data_to_file
from dotenv import load_dotenv, find_dotenv
from typing import Any, Dict
from utils.utils import get_image_url, remove_item_from_list

RUN_LOCAL = False

if RUN_LOCAL:
    dotenv_path = find_dotenv()

    if len(dotenv_path) == 0:
        raise Exception("Environment file not found")

    load_dotenv(dotenv_path)

job_send_toad: Job

INTERVAL = 3600 * 24

persistent_data: Dict[str, Any] = get_data_from_file()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update
# and context. Error handlers also receive the raised TelegramError object in
# error.


def start(update, context):
    """Send a message when the command /start is issued."""
    chat_id = update.effective_chat.id
    if chat_id not in persistent_data['chat_ids']:
        persistent_data['chat_ids'].append(chat_id)

        save_data_to_file(persistent_data)

        if not job_send_toad.enabled:
            job_send_toad.enabled = True

        context.bot.send_message(chat_id=chat_id,
                                 text="Toad delivery has been enabled for your chat!")
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text="Toads already know about this place")


def stop(update, context):
    """Send a message when the command /start is issued."""
    chat_id = update.effective_chat.id

    if chat_id in persistent_data['chat_ids']:
        persistent_data['chat_ids'] = remove_item_from_list(
            persistent_data['chat_ids'], chat_id)

        save_data_to_file(persistent_data)

        context.bot.send_message(chat_id=chat_id,
                                 text="Toads will no longer visit you :c")
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text="Toads already left")


def interval(update, context):
    """Send a message when the command /start is issued."""
    chat_id = update.effective_chat.id
    argument = context.args[0]

    global INTERVAL
    INTERVAL = int(argument)

    context.bot.send_message(chat_id=chat_id,
                             text="Toad interval was set to " + str(INTERVAL))


def help(update, context):
    """Send a message when the command /help is issued."""
    helpText = '''/stop - unsubscribe from the toad goodness. Not recommended\n
    /interval - set toad interval'''
    update.message.reply_text(helpText)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def send_toad(context: CallbackContext):
    global job_send_toad
    global persistent_data

    if len(persistent_data['chat_ids']) == 0:
        job_send_toad.enabled = False
        return

    if persistent_data['image_index'] >= 7796:
        persistent_data['image_index'] = 0

    for id in persistent_data['chat_ids']:
        context.bot.send_photo(chat_id=id,
                               photo=get_image_url(
                                   persistent_data['image_index']),
                               caption='Toad of the day')

    persistent_data['image_index'] += 1

    save_data_to_file(persistent_data)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bots token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    PORT = int(os.getenv('PORT', 5000))
    TOKEN = os.getenv("BOT_TOKEN")

    updater = Updater(token=TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("interval", interval))
    dp.add_handler(CommandHandler("help", help))

    jq = updater.job_queue
    global job_send_toad
    job_send_toad = jq.run_repeating(
        send_toad, interval=INTERVAL, first=0)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    # updater.start_polling()
    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://toad-bot.herokuapp.com/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
