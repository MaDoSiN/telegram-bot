import os
import tempfile
from pytube import YouTube
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8537394978:AAHDcRQOXFKhRsT5qVOR3THpYC1hsVLjCAQ"
CHANNEL = "@MaDoSiNPlus"
MAX_MB = 20  # برای اینکه generous-smile کرش نکنه

# ---------- start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام\n"
        "اول عضو کانال شو:\n"
        "https://t.me/MaDoSiNPlus\n\n"
        "بعد لینک یوتیوب رو بفرست"
    )

# ---------- check join ----------
async def is_member(context, user_id):
    try:
        m = await context.bot.get_chat_member(CHANNEL, user_id)
        return m.status not in ("left", "kicked")
    except:
        return False

# ---------- get link ----------
async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_member(context, update.effective_user.id):
        await update.message.reply_text("❌ اول عضو کانال شو")
        return

    url = update.message.text.strip()
    if "youtu" not in url:
        await update.message.reply_text("❌ لینک یوتیوب معتبر بفرست")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 720p", callback_data="720|" + url)],
        [InlineKeyboardButton("🎧 فقط صدا", callback_data="audio|" + url)],
    ])
    await update.message.reply_text("انتخاب کن:", reply_markup=keyboard)

# ---------- download ----------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quality, url = query.data.split("|", 1)
    await query.edit_message_text("⏳ در حال دانلود...")

    try:
        yt = YouTube(url)
        with tempfile.TemporaryDirectory() as tmp:
            if quality == "audio":
                stream = yt.streams.filter(only_audio=True).first()
            else:
                stream = yt.streams.filter(progressive=True, res="720p", file_extension="mp4").first()

            if not stream:
                await query.message.reply_text("❌ این کیفیت موجود نیست")
                return

            path = stream.download(output_path=tmp)
            size_mb = os.path.getsize(path) / (1024 * 1024)

            if size_mb > MAX_MB:
                await query.message.reply_text("❌ حجم فایل زیاده، قابل ارسال نیست")
                return

            if quality == "audio":
                await query.message.reply_audio(audio=open(path, "rb"))
            else:
                await query.message.reply_video(video=open(path, "rb"))

    except Exception as e:
        await query.message.reply_text("❌ خطا در دانلود")

# ---------- run ----------
def main():
    print("BOT RUNNING...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_link))
    app.add_handler(CallbackQueryHandler(button))

    # ⬅️ این مهم‌ترین خطه (بدون asyncio)
    app.run_polling()

if __name__ == "__main__":
    main()
