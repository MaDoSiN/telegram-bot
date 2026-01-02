import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from pytube import YouTube

TOKEN = "8537394978:AAGfdr-ujXBahs8uIfmHfMa2L7CO1coFvzA"  # توکن ربات

DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# ذخیره وضعیت کاربر برای بررسی جوین کانال
users_ready = {}

CHANNEL_LINK = "https://t.me/MaDoSiNPlus"

# -----------------------------

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    users_ready[chat_id] = False
    update.message.reply_text(
        f"سلام! خوش آمدید!\nلطفا برای استفاده از ربات در کانال جوین شوید:\n{CHANNEL_LINK}"
    )

def check_channel(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    # برای ساده‌سازی، فرض می‌کنیم کاربر جوین شده بعد از هر پیام
    # برای بررسی واقعی می‌توان از تلگرام API استفاده کرد
    if not users_ready.get(chat_id, False):
        users_ready[chat_id] = True
        update.message.reply_text("خب، حالا لینک یوتیوبتون رو بفرستین:")

def handle_youtube(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if not users_ready.get(chat_id, False):
        update.message.reply_text(f"لطفا ابتدا در کانال جوین شوید:\n{CHANNEL_LINK}")
        return

    url = update.message.text
    if 'youtube.com' not in url and 'youtu.be' not in url:
        update.message.reply_text("این لینک یوتیوب نیست! دوباره امتحان کنید.")
        return

    try:
        yt = YouTube(url)
        # ساخت کیبورد با سه گزینه: 720, 1080, صدا
        keyboard = [
            [InlineKeyboardButton("Video 720p", callback_data=f"720|{url}")],
            [InlineKeyboardButton("Video 1080p", callback_data=f"1080|{url}")],
            [InlineKeyboardButton("Audio Only", callback_data=f"audio|{url}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("لطفا کیفیت مورد نظر رو انتخاب کنید:", reply_markup=reply_markup)
    except Exception as e:
        update.message.reply_text(f"خطا در پردازش لینک: {e}")

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    choice, url = query.data.split("|")

    try:
        yt = YouTube(url)
        if choice == "720":
            stream = yt.streams.filter(res="720p", progressive=True).first()
        elif choice == "1080":
            stream = yt.streams.filter(res="1080p", progressive=True).first()
        elif choice == "audio":
            stream = yt.streams.filter(only_audio=True).first()
        else:
            query.edit_message_text("انتخاب نامعتبر")
            return

        if not stream:
            query.edit_message_text("کیفیت مورد نظر موجود نیست.")
            return

        filepath = stream.download(DOWNLOAD_PATH)
        query.edit_message_text(f"دانلود شد: {yt.title}")
        # ارسال فایل به کاربر
        if choice == "audio":
            with open(filepath, "rb") as f:
                context.bot.send_audio(chat_id=query.message.chat.id, audio=f)
        else:
            with open(filepath, "rb") as f:
                context.bot.send_video(chat_id=query.message.chat.id, video=f)
        os.remove(filepath)
    except Exception as e:
        query.edit_message_text(f"خطا: {e}")

# -----------------------------

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_channel))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_youtube))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
