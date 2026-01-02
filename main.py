from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from pytube import YouTube
from flask import Flask
from threading import Thread
import os
import re
import subprocess

TOKEN = "8537394978:AAGfdr-ujXBahs8uIfmHfMa2L7CO1coFvzA"
CHANNEL = "@MaDoSiNPlus"

# ---------------- Keep-Alive ----------------
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is running!"

def run():
    app_web.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# ---------------- Utils ----------------
def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_stream(yt, res):
    """دانلود ویدیو و صدا و merge با ffmpeg"""
    video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', res=res, only_video=True).first()
    audio_stream = yt.streams.filter(only_audio=True).first()
    if not video_stream or not audio_stream:
        return None

    video_file = f"{clean_filename(yt.title)}_video.mp4"
    audio_file = f"{clean_filename(yt.title)}_audio.mp4"
    output_file = f"{clean_filename(yt.title)[:50]}_{res}.mp4"

    video_stream.download(filename=video_file)
    audio_stream.download(filename=audio_file)

    # Merge with ffmpeg
    subprocess.run([
        "ffmpeg", "-y", "-i", video_file, "-i", audio_file, "-c", "copy", output_file
    ])

    # Remove temp files
    os.remove(video_file)
    os.remove(audio_file)

    return output_file

# ---------------- Bot Handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات آماده است.\nلینک یوتیوب بفرست تا دانلود کنم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text

    if "youtube.com" not in text and "youtu.be" not in text:
        await update.message.reply_text("لینک یوتیوب معتبر بفرست!")
        return

    # بررسی عضویت در کانال
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL, user_id=user.id)
        if member.status in ["left", "kicked"]:
            await update.message.reply_text(f"⚠ لطفاً اول عضو کانال {CHANNEL} شو!")
            return
    except:
        await update.message.reply_text("⚠ خطا در بررسی عضویت کانال! مطمئن شو ربات ادمین کانال هست.")
        return

    yt = YouTube(text)
    available = []
    if yt.streams.filter(adaptive=True, file_extension='mp4', res="720p", only_video=True).first():
        available.append("720p")
    if yt.streams.filter(adaptive=True, file_extension='mp4', res="1080p", only_video=True).first():
        available.append("1080p")

    if not available:
        await update.message.reply_text("⚠ هیچ کیفیت مناسب موجود نیست!")
        return

    keyboard = [[InlineKeyboardButton(f"{q}", callback_data=f"{text}|{q}") for q in available]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("کیفیت ویدیو را انتخاب کنید:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url, quality = query.data.split("|")

    try:
        yt = YouTube(url)
        file_path = download_stream(yt, quality)
        if not file_path:
            await query.edit_message_text(f"⚠ کیفیت {quality} موجود نیست!")
            return

        await context.bot.send_video(chat_id=query.message.chat_id, video=open(file_path, "rb"))
        os.remove(file_path)
        await query.edit_message_text(f"✅ دانلود ویدیو با کیفیت {quality} انجام شد!")
    except Exception as e:
        await query.edit_message_text(f"⚠ خطا در دانلود: {e}")

# ---------------- Application ----------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
