import os
from pytube import YouTube
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# ==========================
# ⚠️ حتماً این توکن را با توکن جدید خودت جایگزین کن
TOKEN = "8537394978:AAHjpbH2sXCkVhgRqU2kZAw9Hepcfa0UbA4"
CHANNEL_USERNAME = "@MaDoSiNPlus"
# ==========================

# مسیر موقت (نیازی به ارسال مستقیم فایل نیست)
DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# بررسی جوین کانال
def is_user_joined(bot, user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# دستور استارت
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 سلام! خوش آمدید!\n\n"
        "🔒 لطفا برای استفاده از ربات ابتدا عضو کانال شوید:\n"
        "https://t.me/MaDoSiNPlus\n\n"
        "بعد از جوین، لینک یوتیوب خود را ارسال کنید."
    )

# دریافت لینک یوتیوب
def handle_link(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if not is_user_joined(context.bot, user_id):
        update.message.reply_text(
            "❌ هنوز عضو کانال نشدید. لطفا اول جوین شوید:\n"
            "https://t.me/MaDoSiNPlus"
        )
        return

    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        update.message.reply_text("❌ لینک یوتیوب معتبر نیست.")
        return

    try:
        yt = YouTube(url)
        buttons = []

        # بررسی لینک 720p
        stream_720 = yt.streams.filter(res="720p", progressive=True).first()
        if stream_720:
            buttons.append([InlineKeyboardButton("🎬 720p", url=stream_720.url)])

        # بررسی لینک 360p
        stream_360 = yt.streams.filter(res="360p", progressive=True).first()
        if stream_360:
            buttons.append([InlineKeyboardButton("📹 360p", url=stream_360.url)])

        # فقط صدا
        stream_audio = yt.streams.filter(only_audio=True).first()
        if stream_audio:
            buttons.append([InlineKeyboardButton("🎧 فقط صدا", url=stream_audio.url)])

        if not buttons:
            update.message.reply_text("❌ هیچ لینک دانلود موجود نیست.")
            return

        update.message.reply_text(
            "کیفیت مورد نظر خود را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        update.message.reply_text(f"❌ خطا در پردازش ویدیو: {e}")

# ==========================
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_link))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
