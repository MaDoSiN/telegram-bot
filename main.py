from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from pytube import YouTube
from flask import Flask
from threading import Thread
import os
import re

TOKEN = "8537394978:AAGfdr-ujXBahs8uIfmHfMa2L7CO1coFvzA"
CHANNEL = "@MaDoSiNPlus"

# ---------- Keep-Alive ----------
app_web = Flask('')

@app_web.route('/')
def home():
    return "🤖 Bot Online: Systems Nominal ⚡"

def run():
    app_web.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# ---------- Utilities ----------
def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def get_streams(yt):
    # Progressive streams اولویت
    streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
    if streams:
        return streams
    # Fallback به adaptive 720p
    streams = yt.streams.filter(adaptive=True, file_extension='mp4', res="720p", only_video=True)
    return streams

# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ System Online: YouTube Downloader Active\n"
        "Send a YouTube link to start the transfer protocol."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text

    # Validate YouTube URL
    if "youtube.com" not in text and "youtu.be" not in text:
        await update.message.reply_text("⚠ Invalid YouTube link detected. Send a proper link.")
        return

    # Check channel membership
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL, user_id=user.id)
        if member.status in ["left", "kicked"]:
            await update.message.reply_text(f"⚠ Access Denied: Join {CHANNEL} first. 🚀")
            return
    except:
        await update.message.reply_text("⚠ Membership check failed. Ensure bot is admin in the channel.")
        return

    # Create YouTube object
    try:
        yt = YouTube(text)
    except Exception as e:
        await update.message.reply_text(f"⚠ Error reading YouTube link: {e}")
        return

    # Get streams
    streams = get_streams(yt)
    if not streams:
        await update.message.reply_text("⚠ No downloadable stream available (720p progressive/adaptive missing).")
        return

    # Build buttons
    keyboard = []
    for s in streams:
        keyboard.append([InlineKeyboardButton(f"{s.resolution}", callback_data=f"{s.itag}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚡ Select desired resolution:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    itag = query.data

    try:
        yt = YouTube(query.message.text.split()[0])  # لینک یوتیوب از متن پیام قبلی
        stream = yt.streams.get_by_itag(itag)
        if not stream:
            await query.edit_message_text("⚠ Selected stream unavailable.")
            return

        await query.edit_message_text(f"⏳ Downloading {stream.resolution} video... ⚡")
        file_path = f"{clean_filename(yt.title)[:50]}_{stream.resolution}.mp4"
        stream.download(filename=file_path)

        await context.bot.send_video(chat_id=query.message.chat_id, video=open(file_path, "rb"))
        os.remove(file_path)
        await query.edit_message_text(f"✅ Download complete: {stream.resolution} transferred successfully. 💻")
    except Exception as e:
        await query.edit_message_text(f"⚠ Download error: {e}")

# ---------- Application ----------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
