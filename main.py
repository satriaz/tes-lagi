import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

active_reminders = {}
reminder_counter = 1

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send /set <remaining_energy> to set a reminder when your energy is full.')

def set_timer(update: Update, context: CallbackContext) -> None:
    global reminder_counter
    chat_id = update.message.chat_id
    try:
        remaining_energy = int(context.args[0])
        time_to_full = (240 - remaining_energy) * 6 * 60
        hours, remainder = divmod(time_to_full, 3600)
        minutes, seconds = divmod(remainder, 60)
        context.job_queue.run_once(remind, time_to_full, context=chat_id)
        active_reminders[reminder_counter] = time_to_full
        update.message.reply_text(f'Timer set! Reminder #{reminder_counter} will notify you when your energy is full in about {hours} hours and {minutes} minutes.')
        reminder_counter += 1
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <remaining_energy>')

def remind(context: CallbackContext) -> None:
    job = context.job
    chat_id = job.context
    context.bot.send_message(chat_id, text='Your energy is now full!')
    for reminder_num, remaining_time in active_reminders.items():
        if remaining_time == job.when():
            active_reminders.pop(reminder_num)
            break

def cancel_reminder(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if active_reminders:
        active_reminders.pop(max(active_reminders.keys()))
        update.message.reply_text('Last reminder cancelled.')
    else:
        update.message.reply_text('No active reminders found.')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('/start - Start the bot\n/set <remaining_energy> - Set a reminder when your energy is full\n/cancel - Cancel the last set reminder')

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("set", set_timer))
    dispatcher.add_handler(CommandHandler("cancel", cancel_reminder))
    dispatcher.add_handler(CommandHandler("help", help_command))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
