from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from pytube import YouTube
from flask import Flask
from threading import Thread
import os 
import re

def clean_filename(name):
    # حذف کاراکترهای غیرمجاز برای ویندوز
    return re.sub(r'[\\/*?:"<>|]', "", name)


TOKEN = "8537394978:AAGfdr-ujXBahs8uIfmHfMa2L7CO1coFvzA"
CHANNEL = "@MaDoSiNPlus"  # کانال اجباری

# ---- Keep Alive ----
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

# ---- Bot ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات آماده است.\nلینک یوتیوب بفرست تا دانلود کنم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text

    # بررسی لینک یوتیوب
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

    # ارسال گزینه کیفیت
    keyboard = [
        [
            InlineKeyboardButton("720p", callback_data=f"{text}|720"),
            InlineKeyboardButton("1080p", callback_data=f"{text}|1080")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("کیفیت ویدیو را انتخاب کنید:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url, quality = query.data.split("|")

    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4', res=quality).first()
        if not stream:
            await query.edit_message_text("⚠ کیفیت انتخاب شده موجود نیست!")
            return

        file_path = f"{clean_filename(yt.title)[:50]}.mp4"
stream.download(filename=file_path)


        await context.bot.send_video(chat_id=query.message.chat_id, video=open(file_path, "rb"))
        os.remove(file_path)  # حذف فایل بعد از ارسال
        await query.edit_message_text(f"دانلود ویدیو با کیفیت {quality} انجام شد!")
    except Exception as e:
        await query.edit_message_text(f"⚠ خطا در دانلود: {e}")

# ---- Application ----
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
