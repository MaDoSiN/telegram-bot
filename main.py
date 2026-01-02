from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from pytube import YouTube
from flask import Flask
from threading import Thread
import re
import os

# ================= CONFIG =================
TOKEN = "8537394978:AAGfdr-ujXBahs8uIfmHfMa2L7CO1coFvzA"
CHANNEL_USERNAME = "@MaDoSiNPlus"

# ================= KEEP ALIVE =================
app = Flask("")

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_web).start()

# ================= UTILS =================
def extract_youtube_url(text: str):
    patterns = [
        r"(https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+)",
        r"(https?://youtu\.be/[\w-]+)",
        r"(https?://(?:www\.)?youtube\.com/shorts/[\w-]+)"
    ]
    for p in patterns:
        match = re.search(p, text)
        if match:
            url = match.group(0)
            # تبدیل Shorts به لینک عادی
            if "shorts" in url:
                video_id = url.split("/")[-1]
                url = f"https://www.youtube.com/watch?v={video_id}"
            return url
    return None

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ ربات دانلود یوتیوب فعال شد\n\n"
        "🔗 لینک یوتیوب (عادی یا Shorts) رو بفرست\n"
        "🎬 کیفیت انتخاب کن، دانلود کن"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user

    url = extract_youtube_url(text)
    if not url:
        await update.message.reply_text("⚠ لینک یوتیوب معتبر نیست!")
        return

    # ---------- JOIN CHECK ----------
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user.id)
        if member.status in ["left", "kicked"]:
            await update.message.reply_text(
                f"❗ برای استفاده از ربات ابتدا عضو کانال شو:\n{CHANNEL_USERNAME}"
            )
            return
    except:
        await update.message.reply_text("⚠ خطا در بررسی عضویت (ربات ادمین نیست)")
        return

    # ---------- YOUTUBE ----------
    try:
        yt = YouTube(url)
        context.user_data["yt_url"] = url
    except Exception as e:
        await update.message.reply_text("⚠ خطا در پردازش لینک یوتیوب")
        return

    keyboard = []

    # progressive (720)
    prog = yt.streams.filter(progressive=True, file_extension="mp4")
    if prog:
        s720 = prog.filter(res="720p").first()
        if s720:
            keyboard.append([InlineKeyboardButton("🎥 720p", callback_data=s720.itag)])

    # adaptive 1080
    vid1080 = yt.streams.filter(res="1080p", adaptive=True, only_video=True).first()
    if vid1080:
        keyboard.append([InlineKeyboardButton("🎬 1080p", callback_data=vid1080.itag)])

    # audio
    audio = yt.streams.filter(only_audio=True).first()
    if audio:
        keyboard.append([InlineKeyboardButton("🎧 فقط صدا", callback_data=audio.itag)])

    if not keyboard:
        await update.message.reply_text("⚠ کیفیت قابل دانلود پیدا نشد")
        return

    await update.message.reply_text(
        "⚙ کیفیت مورد نظر رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    itag = query.data
    url = context.user_data.get("yt_url")

    if not url:
        await query.edit_message_text("⚠ لینک منقضی شده، دوباره بفرست")
        return

    yt = YouTube(url)
    stream = yt.streams.get_by_itag(itag)

    if not stream:
        await query.edit_message_text("⚠ این کیفیت در دسترس نیست")
        return

    await query.edit_message_text("⏳ در حال دانلود...")

    filename = clean_filename(yt.title)[:50]
    path = stream.download(filename=filename)

    if stream.only_audio:
        await context.bot.send_audio(
            chat_id=query.message.chat_id,
            audio=open(path, "rb"),
            title=yt.title
        )
    else:
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=open(path, "rb"),
            supports_streaming=True
        )

    os.remove(path)

# ================= RUN =================
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(handle_button))

application.run_polling()
