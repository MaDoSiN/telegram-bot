from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from pytube import YouTube
from flask import Flask
from threading import Thread
import os
import re

# ---------------- Configuration ----------------
TOKEN = "8537394978:AAGfdr-ujXBahs8uIfmHfMa2L7CO1coFvzA"
CHANNEL = "@MaDoSiNPlus"

# ---------------- Keep-Alive ----------------
app_web = Flask('')

@app_web.route('/')
def home():
    return "🤖 Bot Online: Systems Nominal ⚡"

def run_web():
    app_web.run(host='0.0.0.0', port=8080)

Thread(target=run_web).start()

# ---------------- Utilities ----------------
def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def extract_youtube_url(text):
    pattern = r"(https?://(?:www\.)?youtu(?:\.be/|be\.com/watch\?v=)[\w-]+)"
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None

def get_streams(yt):
    # Progressive streams first
    streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
    if streams:
        return streams
    # Adaptive 720p fallback
    streams = yt.streams.filter(adaptive=True, file_extension='mp4', res="720p", only_video=True)
    # Audio-only fallback
    if not streams:
        streams = yt.streams.filter(only_audio=True, file_extension='mp4')
    return streams

# ---------------- Handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ سلام! خوش آمدید. لینک یوتیوب رو برام بفرست تا واست دانلود کنم ⚡"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text

    # Extract YouTube URL
    url = extract_youtube_url(text)
    if not url:
        await update.message.reply_text("⚠ لینک یوتیوب معتبر نیست! دوباره امتحان کنید.")
        return

    # Check channel membership
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL, user_id=user.id)
        if member.status in ["left", "kicked"]:
            await update.message.reply_text(f"⚠ دسترسی ندارید! ابتدا در کانال {CHANNEL} جوین شوید.")
            return
    except:
        await update.message.reply_text("⚠ خطا در بررسی عضویت. ربات باید ادمین کانال باشد.")
        return

    # Create YouTube object
    try:
        yt = YouTube(url)
    except Exception as e:
        await update.message.reply_text(f"⚠ خطا در خواندن لینک یوتیوب: {e}")
        return

    # Get streams
    streams = get_streams(yt)
    if not streams:
        await update.message.reply_text("⚠ هیچ استریم دانلودی در دسترس نیست (720p/1080p/adaptive).")
        return

    # Store URL for callback
    context.user_data["yt_url"] = url

    # Build buttons
    keyboard = []
    for s in streams:
        label = s.resolution if s.resolution else "Audio 🎵"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"{s.itag}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚡ کیفیت مورد نظر را انتخاب کنید:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    itag = query.data

    url = context.user_data.get("yt_url")
    if not url:
        await query.edit_message_text("⚠ لینک اصلی یافت نشد.")
        return

    try:
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(itag)
        if not stream:
            await query.edit_message_text("⚠ استریم انتخابی موجود نیست.")
            return

        await query.edit_message_text(f"⏳ در حال دانلود {stream.resolution if stream.resolution else 'Audio'}... ⚡")
        file_path = f"{clean_filename(yt.title)[:50]}_{stream.resolution if stream.resolution else 'audio'}.mp4"
        stream.download(filename=file_path)

        await context.bot.send_video(chat_id=query.message.chat_id, video=open(file_path, "rb"))
        os.remove(file_path)
        await query.edit_message_text(f"✅ دانلود کامل شد و ارسال شد: {stream.resolution if stream.resolution else 'Audio'} 💻")
    except Exception as e:
        await query.edit_message_text(f"⚠ خطا در دانلود: {e}")

# ---------------- Application ----------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
