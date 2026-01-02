from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytube import YouTube
import os

API_ID = 123456  # اینو از my.telegram.org بگیر
API_HASH = "your_api_hash"  # اینم از my.telegram.org
BOT_TOKEN = 8537394978:AAGfdr-ujXBahs8uIfmHfMa2L7CO1coFvzA  # **توکن جدید** بزار

CHANNEL_USERNAME = "@MaDoSiNPlus"

app = Client("youtube_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# استارت و خوش آمدگویی
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        f"سلام {message.from_user.first_name}! لطفا ابتدا عضو کانال {CHANNEL_USERNAME} شوید و بعد لینک یوتیوب خود را ارسال کنید."
    )

# دریافت لینک یوتیوب
@app.on_message(filters.text & ~filters.command)
async def youtube_handler(client, message):
    # چک عضویت کانال
    member = await client.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
    if member.status in ["left", "kicked"]:
        await message.reply_text(f"⚠ لطفا ابتدا عضو کانال {CHANNEL_USERNAME} شوید.")
        return

    url = message.text
    # بررسی لینک یوتیوب ساده
    if "youtube.com" not in url and "youtu.be" not in url:
        await message.reply_text("لینک یوتیوب معتبر وارد کنید.")
        return

    # دکمه‌های کیفیت
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("720p", callback_data=f"720|{url}")],
            [InlineKeyboardButton("1080p", callback_data=f"1080|{url}")],
            [InlineKeyboardButton("فقط صدا", callback_data=f"audio|{url}")],
        ]
    )
    await message.reply_text("کیفیت مورد نظر خود را انتخاب کنید:", reply_markup=buttons)

# پردازش انتخاب کیفیت
@app.on_callback_query()
async def callback(client, callback_query):
    data = callback_query.data
    quality, url = data.split("|")

    await callback_query.message.edit_text("در حال آماده‌سازی ویدیو ... لطفا صبر کنید.")

    try:
        yt = YouTube(url)
        if quality == "audio":
            stream = yt.streams.filter(only_audio=True).first()
        else:
            stream = yt.streams.filter(res=quality, progressive=True).first()
        
        file_path = stream.download()
        await client.send_video(callback_query.from_user.id, file_path) if quality != "audio" else await client.send_audio(callback_query.from_user.id, file_path)
        os.remove(file_path)
        await callback_query.message.edit_text("✅ فایل ارسال شد.")
    except Exception as e:
        await callback_query.message.edit_text(f"❌ خطا در دانلود: {e}")

app.run()
