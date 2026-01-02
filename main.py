from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8537394978:AAGfdr-ujXBahs8uIfmHfMa2L7CO1coFvzA"  # توکن رباتت

def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! ربات آماده است.")

updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.start_polling()
updater.idle()
