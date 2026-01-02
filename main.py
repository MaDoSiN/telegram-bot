from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from pytube import YouTube
from flask import Flask
from threading import Thread
import os
import re

TOKEN = "8537394978:AAGfdr-ujXBahs8uIfmHfMa2L7CO1coFvzA"
CHANNEL = "@MaDoSiNPlus"

# ---------------- Keep-Alive ----------------
app_web = Flask('')

@app_web.route('/')
def home():
    return "🤖 Bot Online: Systems Nominal ⚡"

def run():
    app_web.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# ---------------- Utils ----------------
def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def get_progressive_stream(yt):
    return yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

# ---------------- Handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💻 System Active: YouTube Downloader Online ⚡\n"
        "Send a YouTube link to initiate the transfer protocol."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text

    # Check for YouTube URL
    if "youtube.com" not in text and "youtu.be" not in text:
        await update.message.reply_text("⚠ Invalid YouTube link detected. 🔗")
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

    # Build YouTube object
    try:
        yt = YouTube(text)
    except Exception as e:
        await update.message.reply_text(f"⚠ YouTube URL Error: {e}")
        return

    # Get progressive stream
    stream = get_progressive_stream(yt)
    if not stream:
        await update.message.reply_text("⚠ No downloadable stream available (720p progressive missing).")
        return

    keyboard = [[InlineKeyboardButton(f"{stream.resolution}", callback_data=f"{text}|{stream.resolution}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚡ Select your desired resolution:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url, quality = query.data.split("|")

    try:
        yt = YouTube(url)
        await query.edit_message_text(f"⏳ Downloading {quality} video... Please wait. ⚡")
        stream = yt.streams.filter(progressive=True, file_extension='mp4', res=quality).first()
        if not stream:
            await query.edit_message_text(f"⚠ Resolution {quality} not available.")
            return

        file_path = f"{clean_filename(yt.title)[:50]}_{quality}.mp4"
        stream.download(filename=file_path)
        await context.bot.send_video(chat_id=query.message.chat_id, video=open(file_path, "rb"))
        os.remove(file_path)
        await query.edit_message_text(f"✅ Download complete: {quality} transferred successfully. 💻")
    except Exception as e:
        await query.edit_message_text(f"⚠ Download error: {e}")

# ---------------- Application ----------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
