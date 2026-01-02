import os
from pytube import YouTube
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler
)

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_USERNAME = "@MaDoSiNPlus"
DOWNLOAD_PATH = "downloads"

os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# ------------------ ابزارها ------------------

def is_user_joined(bot, user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ------------------ دستورات ------------------

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 سلام خوش اومدی\n\n"
        "🔒 برای استفاده از ربات اول باید عضو کانال بشی:\n"
        "https://t.me/MaDoSiNPlus\n\n"
        "بعد از جوین، لینک یوتیوب رو بفرست"
    )

def handle_link(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if not is_user_joined(context.bot, user_id):
        update.message.reply_text(
            "❌ هنوز عضو کانال نشدی\n"
            "اول جوین شو 👇\n"
            "https://t.me/MaDoSiNPlus"
        )
        return

    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:
        update.message.reply_text("❌ لینک یوتیوب معتبر نیست")
        return

    try:
        yt = YouTube(url)

        buttons = []

        if yt.streams.filter(res="720p", progressive=True).first():
            buttons.append(
                [InlineKeyboardButton("🎬 720p", callback_data=f"720|{url}")]
            )

        if yt.streams.filter(only_audio=True).first():
            buttons.append(
                [InlineKeyboardButton("🎧 فقط صدا", callback_data=f"audio|{url}")]
            )

        if not buttons:
            update.message.reply_text("❌ کیفیت قابل دانلود پیدا نشد")
            return

        update.message.reply_text(
            "کیفیت مورد نظر رو انتخاب کن 👇",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception:
        update.message.reply_text("❌ خطا در پردازش ویدیو")

# ------------------ دکمه‌ها ------------------

def download_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    choice, url = query.data.split("|")

    try:
        yt = YouTube(url)

        if choice == "720":
            stream = yt.streams.filter(res="720p", progressive=True).first()
        else:
            stream = yt.streams.filter(only_audio=True).first()

        if not stream:
            query.edit_message_text("❌ این کیفیت موجود نیست")
            return

        query.edit_message_text("⬇️ در حال دانلود...")

        filepath = stream.download(DOWNLOAD_PATH)

        if choice == "audio":
            with open(filepath, "rb") as f:
                context.bot.send_audio(query.message.chat.id, audio=f)
        else:
            with open(filepath, "rb") as f:
                context.bot.send_video(query.message.chat.id, video=f)

        os.remove(filepath)

    except Exception:
        query.edit_message_text("❌ خطا در دانلود یا ارسال فایل")

# ------------------ اجرا ------------------

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_link))
    dp.add_handler(CallbackQueryHandler(download_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
