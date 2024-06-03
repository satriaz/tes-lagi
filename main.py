import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = '7499366859:AAEQS4vSRxoCawlMypQ7ZtYryHRn_1Uso2M'
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
        update.message.reply_text(f'Timer {reminder_counter} set! I will remind you when your energy is full in about {hours} hours and {minutes} minutes.')
        reminder_counter += 1

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <remaining_energy>')

def remind(context: CallbackContext) -> None:
    job = context.job
    chat_id = job.context
    context.bot.send_message(chat_id, text='Your energy is now full!')
    if chat_id in active_reminders.values():
        active_reminders.pop(chat_id)

def cancel_reminder(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        reminder_number = int(context.args[0])
        if reminder_number in active_reminders:
            active_reminders.pop(reminder_number)
            update.message.reply_text(f'Reminder {reminder_number} cancelled.')
        else:
            update.message.reply_text(f'Reminder {reminder_number} not found.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /cancel <reminder_number>')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('/start - Start the bot\n/set <remaining_energy> - Set a reminder when your energy is full\n/cancel <reminder_number> - Cancel a specific reminder')

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
