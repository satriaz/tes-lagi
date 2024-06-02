import subprocess
subprocess.run(["pip", "install", "python-telegram-bot==13.5"])
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Replace 'YOUR_TOKEN' with your actual bot token
TOKEN = '7499366859:AAEQS4vSRxoCawlMypQ7ZtYryHRn_1Uso2M'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send /set <remaining_energy> to set a reminder when your energy is full.')

# This function will be called when the /set command is issued
def set_timer(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        remaining_energy = int(context.args[0])
        time_to_full = (240 - remaining_energy) * 6 * 60
        hours, remainder = divmod(time_to_full, 3600)
        minutes, seconds = divmod(remainder, 60)
        context.job_queue.run_once(remind, time_to_full, context=chat_id)
        update.message.reply_text(f'Timer set! I will remind you when your energy is full in about {hours} hours and {minutes} minutes.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <remaining_energy>')

# This function will send the reminder message when the timer is up
def remind(context: CallbackContext) -> None:
    job = context.job
    context.bot.send_message(job.context, text='Your energy is now full!')

def main() -> None:
    while True:
        try:
            updater = Updater(TOKEN)

            dispatcher = updater.dispatcher

            dispatcher.add_handler(CommandHandler("start", start))
            dispatcher.add_handler(CommandHandler("set", set_timer))

            updater.start_polling()

            updater.idle()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)  # Wait for 5 seconds before restarting the loop

if __name__ == '__main__':
    main()