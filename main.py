from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from pytube import YouTube
from flask import Flask
from threading import Thread
import os
import re

# ---------- تنظیمات ----------
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

def extract_youtube_url(text):
    text = text.strip()
    pattern = r"(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w\-]+(?:[&?][\w=%\-]*)*)"
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None

def get_streams(yt):
    streams = []
    # Progressive video+audio
    streams += yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
    # Adaptive video (احتمالا بدون صدا)
    streams += yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True, res="720p")
    streams += yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True, res="1080p")
    # Audio-only
    streams += yt.streams.filter(only_audio=True, file_extension='mp4')
    return streams

# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ System Online: YouTube Downloader Active\n"
        "سلام! لینک یوتیوبتون رو برام بفرستین تا براتون آماده کنم."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text

    # شناسایی لینک یوتیوب
    yt_url = extract_youtube_url(text)
    if not yt_url:
        await update.message.reply_text("⚠ لینک یوتیوب معتبر نیست! دوباره امتحان کنید.")
        return

    # ذخیره لینک برای استفاده در callback
    context.user_data["yt_url"] = yt_url

    # بررسی عضویت کانال
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL, user_id=user.id)
        if member.status in ["left", "kicked"]:
            await update.message.reply_text(f"⚠ دسترسی ممنوع: لطفا اول عضو {CHANNEL} بشین! 🚀")
            return
    except:
        await update.message.reply_text("⚠ بررسی عضویت ناموفق بود. مطمئن شو ربات admin کانال هست.")
        return

    # ایجاد شی YouTube
    try:
        yt = YouTube(yt_url)
    except Exception as e:
        await update.message.reply_text(f"⚠ خطا در خواندن لینک: {e}")
        return

    # دریافت استریم‌ها
    streams = get_streams(yt)
    if not streams:
        await update.message.reply_text("⚠ هیچ استریم قابل دانلودی موجود نیست!")
        return

    # ساخت دکمه‌ها
    keyboard = []
    for s in streams:
        if s.includes_audio_track:
            label = f"{s.resolution} + صدا" if hasattr(s, "resolution") else "صدا فقط"
        else:
            label = f"{s.resolution} (بدون صدا)" if hasattr(s, "resolution") else "ویدیو"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"{s.itag}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚡ لطفا کیفیت مورد نظر رو انتخاب کنید:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    itag = query.data
    yt_url = context.user_data.get("yt_url")

    if not yt_url:
        await query.edit_message_text("⚠ لینک یوتیوب پیدا نشد! دوباره امتحان کنید.")
        return

    try:
        yt = YouTube(yt_url)
        stream = yt.streams.get_by_itag(itag)
        if not stream:
            await query.edit_message_text("⚠ استریم انتخاب شده موجود نیست.")
            return

        await query.edit_message_text(f"⏳ در حال دانلود {stream.resolution if hasattr(stream,'resolution') else 'صدا'} ... ⚡")
        file_path = f"{clean_filename(yt.title)[:50]}_{stream.resolution if hasattr(stream,'resolution') else 'audio'}.mp4"
        stream.download(filename=file_path)

        await context.bot.send_video(chat_id=query.message.chat_id, video=open(file_path, "rb"))
        os.remove(file_path)
        await query.edit_message_text(f"✅ دانلود با موفقیت انجام شد: {stream.resolution if hasattr(stream,'resolution') else 'audio'} ⚡")
    except Exception as e:
        await query.edit_message_text(f"⚠ خطا در دانلود: {e}")

# ---------- Application ----------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
