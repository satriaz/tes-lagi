import time
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = '7499366859:AAEQS4vSRxoCawlMypQ7ZtYryHRn_1Uso2M'

active_reminders = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send /set <remaining_energy> to set a reminder when your energy is full.')

def set_timer(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        remaining_energy = int(context.args[0])
        time_to_full = (240 - remaining_energy) * 6 * 60
        hours, remainder = divmod(time_to_full, 3600)
        minutes, seconds = divmod(remainder, 60)
        context.job_queue.run_once(remind, time_to_full, context=chat_id)
        if chat_id not in active_reminders:
            active_reminders[chat_id] = []
        active_reminders[chat_id].append(time_to_full)
        update.message.reply_text(f'Timer set! I will remind you when your energy is full in about {hours} hours and {minutes} minutes.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <remaining_energy>')

def remind(context: CallbackContext) -> None:
    job = context.job
    chat_id = job.context
    context.bot.send_message(chat_id, text='Your energy is now full!')
    if chat_id in active_reminders:
        active_reminders[chat_id].remove(job.remaining_time)

def cancel_reminder(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if chat_id in active_reminders:
        if len(active_reminders[chat_id]) > 1:
            active_reminders[chat_id].pop()
            update.message.reply_text('Reminder cancelled.')
        else:
            active_reminders[chat_id].clear()
            update.message.reply_text('All reminders cancelled.')
    else:
        update.message.reply_text('No active reminders found.')

def list_reminders(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if chat_id in active_reminders:
        if active_reminders[chat_id]:
            reminders_list = '\n'.join([f'Reminder {i+1}: {time_to_full//3600} hours and {(time_to_full%3600)//60} minutes' for i, time_to_full in enumerate(active_reminders[chat_id])])
            update.message.reply_text(f'Active reminders:\n{reminders_list}')
        else:
            update.message.reply_text('No active reminders found.')
    else:
        update.message.reply_text('No active reminders found.')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('/start - Start the bot\n/set <remaining_energy> - Set a reminder when your energy is full\n/cancel - Cancel the last set reminder\n/list - List active reminders')

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
