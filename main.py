import os
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from pytube import YouTube

# ======= تنظیمات =======
BOT_TOKEN = "8537394978:AAHjpbH2sXCkVhgRqU2kZAw9Hepcfa0UbA4"
CHANNEL = "@MaDoSiNPlus"
MAX_FILE_SIZE_MB = 20  # حداکثر حجم مطمئن برای محیط محدود

# ======= چک عضویت کانال =======
async def is_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False

# ======= دستور /start =======
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
    if
