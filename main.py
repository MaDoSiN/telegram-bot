from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import yt_dlp
import os

TOKEN = "8537394978:AAGfdr-ujXBahs8uIfmHfMa2L7CO1coFvzA"
CHANNEL = "@MaDoSiNPlus"

async def is_joined(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 خوش اومدی\n"
        "📌 اول داخل کانال جوین شو:\n"
        "https://t.me/MaDoSiNPlus\n\n"
        "بعد لینک یوتیوب رو بفرست"
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_joined(context.bot, update.effective_user.id):
        await update.message.reply_text("❌ اول باید داخل کانال جوین بشی")
        return

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
