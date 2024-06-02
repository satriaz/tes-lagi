from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters

TOKEN = '7499366859:AAEQS4vSRxoCawlMypQ7ZtYryHRn_1Uso2M'
active_reminders = {}

SELECT_REMINDER, SELECT_CANCEL = range(2)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send /set <remaining_energy> to set a reminder when your energy is full.')

def set_timer(update: Update, context: CallbackContext) -> None:
    # Existing set_timer function
    pass

def remind(context: CallbackContext) -> None:
    # Existing remind function
    pass

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
