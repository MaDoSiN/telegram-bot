from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import yt_dlp
import os

TOKEN = "8537394978:AAHjpbH2sXCkVhgRqU2kZAw9Hepcfa0UbA4"
CHANNEL = "@MaDoSiNPlus"

async def is_joined(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        "🤖 سلام رفیق!\n\n"
        "برای استفاده از ربات باید اول عضو کانالمون بشی 🏷️\n\n"
        "🔗 روی دکمه زیر کلیک کن:"
    )

    keyboard = [
        [InlineKeyboardButton("🤖 جوین کانال", url="https://t.me/MaDoSiNPlus")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, reply_markup=reply_markup)



async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # بررسی عضویت در کانال
    try:
        member = await context.bot.get_chat_member("@MaDoSiNPlus", user_id)
        if member.status not in ["member", "administrator", "creator"]:
            await update.message.reply_text("❌ اول باید عضو کانال بشی!")
            return
    except:
        await update.message.reply_text("❌ خطا در بررسی عضویت، دوباره تلاش کن.")
        return

    # پاک کردن پیام خوش آمدگویی (فرض می‌کنیم پیام قبلی آخرین پیام ربات است)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id - 1)
    except:
        pass  # اگر پاک کردن ممکن نبود، کرش نکنه

    # پیام جدید
    await update.message.reply_text("✅ خب الان لینک یوتیوبت رو بفرست 🤖⬇️")


    url = update.message.text
    if "youtu" not in url:
        await update.message.reply_text("❌ لینک یوتیوب معتبر نیست")
        return

    keyboard = [
        [InlineKeyboardButton("🎬 720p", callback_data=f"720|{url}")],
        [InlineKeyboardButton("🎧 فقط صدا", callback_data=f"audio|{url}")]
    ]
    await update.message.reply_text(
        "کیفیت رو انتخاب کن 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quality, url = query.data.split("|")
    filename = "file.mp4"

    ydl_opts = {
        "outtmpl": filename,
        "format": "best[height<=720]/bestaudio" if quality == "720" else "bestaudio",
        "quiet": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await query.message.reply_document(open(filename, "rb"))
    except Exception as e:
        await query.message.reply_text("❌ خطا در دانلود (احتمالاً حجم بالا)")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(download))
    app.run_polling()
