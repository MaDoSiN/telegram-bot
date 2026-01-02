from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from pytube import YouTube
import os

BOT_TOKEN = "8537394978:AAHjpbH2sXCkVhgRqU2kZAw9Hepcfa0UbA4"
CHANNEL = "@MaDoSiNPlus"

# ---------- چک عضویت ----------
async def is_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False

# ---------- start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 خوش اومدی!\n"
        "اول عضو کانال شو:\n"
        f"https://t.me/{CHANNEL.replace('@','')}\n"
        "بعد لینک یوتیوب رو بفرست."
    )

# ---------- دریافت لینک ----------
async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_member(context, update.effective_user.id):
        await update.message.reply_text(
            f"❌ اول باید عضو کانال بشی:\nhttps://t.me/{CHANNEL.replace('@','')}"
        )
        return

    url = update.message.text
    if "youtu" not in url:
        await update.message.reply_text("❌ لینک یوتیوب معتبر بفرست")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 720p", callback_data=f"720|{url}")],
        [InlineKeyboardButton("🎬 1080p", callback_data=f"1080|{url}")],
        [InlineKeyboardButton("🎧 فقط صدا", callback_data=f"audio|{url}")]
    ])

    await update.message.reply_text("کیفیت رو انتخاب کن:", reply_markup=keyboard)

# ---------- دانلود ----------
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quality, url = query.data.split("|")
    await query.edit_message_text("⏳ در حال دانلود...")

    try:
        yt = YouTube(url)
        if quality == "audio":
            stream = yt.streams.filter(only_audio=True).first()
        else:
            stream = yt.streams.filter(res=quality, file_extension="mp4").first()

        if not stream:
            await query.edit_message_text("❌ این کیفیت موجود نیست")
            return

        file_path = stream.download()

        if quality == "audio":
            await context.bot.send_audio(chat_id=query.from_user.id, audio=open(file_path, "rb"))
        else:
            await context.bot.send_video(chat_id=query.from_user.id, video=open(file_path, "rb"))

        os.remove(file_path)
        await query.edit_message_text("✅ ارسال شد")
    except Exception as e:
        await query.edit_message_text(f"❌ خطا در دانلود: {e}")

# ---------- اجرا ----------
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_link))
    app.add_handler(CallbackQueryHandler(download))
    await app.run_polling()

import asyncio
asyncio.run(main())
