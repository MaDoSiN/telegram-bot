from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from pytube import YouTube
import os

CHANNEL_LINK = "https://t.me/MaDoSiNPlus"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # چک کردن جوین شدن در کانال (میتونی با Telegram Bot API Channel Membership بررسی کنی)
    await update.message.reply_text(
        f"سلام {user.first_name}! برای ادامه باید ابتدا به چنل ما جوین شوی:\n{CHANNEL_LINK}\n\nبعد لینک یوتیوب را ارسال کن."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("لطفاً یک لینک یوتیوب معتبر ارسال کنید.")
        return

    # ساخت دکمه‌های کیفیت
    keyboard = [
        [InlineKeyboardButton("1080p", callback_data=f"{url}|1080")],
        [InlineKeyboardButton("720p", callback_data=f"{url}|720")],
        [InlineKeyboardButton("فقط صدا", callback_data=f"{url}|audio")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("کیفیت مورد نظر را انتخاب کنید:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url, choice = query.data.split("|")
    
    try:
        yt = YouTube(url)
        if choice == "audio":
            stream = yt.streams.filter(only_audio=True).first()
        else:
            stream = yt.streams.filter(res=choice, file_extension="mp4").first()
        
        file_path = stream.download()
        await query.message.reply_document(open(file_path, 'rb'))
        os.remove(file_path)
    except Exception as e:
        await query.message.reply_text(f"مشکلی پیش آمد: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token("8537394978:AAHjpbH2sXCkVhgRqU2kZAw9Hepcfa0UbA4").build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot started...")
    app.run_polling()
