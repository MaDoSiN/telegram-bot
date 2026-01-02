import os
import asyncio
import tempfile
import ffmpeg
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from pytube import YouTube

# ======= تنظیمات =======
BOT_TOKEN = "8537394978:AAHjpbH2sXCkVhgRqU2kZAw9Hepcfa0UbA4"
CHANNEL = "@MaDoSiNPlus"
MAX_FILE_SIZE_MB = 2000  # حداکثر حجم قابل ارسال تلگرام (2GB)

# ======= بررسی عضویت کانال =======
async def is_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False

# ======= استارت =======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 سلام {update.effective_user.first_name}!\n\n"
        f"اول عضو کانال شو:\nhttps://t.me/{CHANNEL.replace('@','')}\n"
        "بعد لینک یوتیوب رو بفرست."
    )

# ======= دریافت لینک =======
async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_member(context, update.effective_user.id):
        await update.message.reply_text(
            f"❌ اول باید عضو کانال بشی:\nhttps://t.me/{CHANNEL.replace('@','')}"
        )
        return

    url = update.message.text.strip()
    if "youtu" not in url:
        await update.message.reply_text("❌ لینک یوتیوب معتبر بفرست")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 720p", callback_data=f"720|{url}")],
        [InlineKeyboardButton("🎬 1080p", callback_data=f"1080|{url}")],
        [InlineKeyboardButton("🎧 فقط صدا", callback_data=f"audio|{url}")]
    ])

    await update.message.reply_text("کیفیت رو انتخاب کن:", reply_markup=keyboard)

# ======= دانلود و ترکیب و ارسال =======
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    quality, url = query.data.split("|")
    await query.edit_message_text("⏳ در حال آماده‌سازی دانلود...")

    try:
        yt = YouTube(url)

        # ایجاد فولدر موقت برای ذخیره فایل‌ها
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path, audio_path, final_path = None, None, None

            if quality == "audio":
                stream = yt.streams.filter(only_audio=True).first()
                audio_path = stream.download(output_path=tmpdir)
                size_mb = os.path.getsize(audio_path) / (1024*1024)
                if size_mb > MAX_FILE_SIZE_MB:
                    await query.edit_message_text("❌ حجم فایل بیشتر از حد مجاز است")
                    return
                await context.bot.send_audio(chat_id=query.from_user.id, audio=open(audio_path, "rb"))
            else:
                # انتخاب بهترین کیفیت تصویری
                video_stream = yt.streams.filter(res=quality, only_video=True).first()
                audio_stream = yt.streams.filter(only_audio=True).first()
                
                if not video_stream or not audio_stream:
                    await query.edit_message_text("❌ کیفیت انتخابی موجود نیست")
                    return

                video_path = video_stream.download(output_path=tmpdir, filename="video.mp4")
                audio_path = audio_stream.download(output_path=tmpdir, filename="audio.mp4")
                final_path = os.path.join(tmpdir, "final.mp4")

                # ترکیب ویدیو و صدا با ffmpeg
                ffmpeg.input(video_path).output(audio_path, final_path, vcodec='copy', acodec='aac', strict='experimental').run(overwrite_output=True)

                size_mb = os.path.getsize(final_path) / (1024*1024)
                if size_mb > MAX_FILE_SIZE_MB:
                    await query.edit_message_text("❌ حجم فایل ترکیبی بیش از حد مجاز است")
                    return

                await context.bot.send_video(chat_id=query.from_user.id, video=open(final_path, "rb"))

        await query.edit_message_text("✅ ارسال شد!")

    except Exception as e:
        await query.edit_message_text(f"❌ خطا: {e}")

# ======= اجرای ربات =======
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_link))
    app.add_handler(CallbackQueryHandler(download))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
