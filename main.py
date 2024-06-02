from telegram import Update, ReplyKeyboardMarkup  # Added import statement
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters

TOKEN = '7499366859:AAEQS4vSRxoCawlMypQ7ZtYryHRn_1Uso2M'
active_reminders = {}

SELECT_REMINDER, SELECT_CANCEL = range(2)

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

def cancel(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send /list to view active reminders.')

def list_reminder(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    if chat_id in active_reminders and active_reminders[chat_id]:
        reminder_keyboard = [[str(reminder) for reminder in active_reminders[chat_id]]]
        update.message.reply_text('Select reminder to cancel:', reply_markup=ReplyKeyboardMarkup(reminder_keyboard, one_time_keyboard=True))
        return SELECT_REMINDER
    else:
        update.message.reply_text('No active reminders to list.')
        return ConversationHandler.END

def select_reminder(update: Update, context: CallbackContext) -> int:
    selected_reminder = int(update.message.text)
    chat_id = update.message.chat_id
    if chat_id in active_reminders and selected_reminder in active_reminders[chat_id]:
        active_reminders[chat_id].remove(selected_reminder)
        update.message.reply_text('Reminder cancelled.')
    else:
        update.message.reply_text('Invalid reminder selection.')
    return ConversationHandler.END

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('This is the help command.')

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Existing handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("set", set_timer))
    dispatcher.add_handler(CommandHandler("cancel", cancel))
    dispatcher.add_handler(CommandHandler("help", help_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('list', list_reminder)],
        states={
            SELECT_REMINDER: [MessageHandler(Filters.text & ~Filters.command, select_reminder)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
