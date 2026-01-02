from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8537394978:AAHDcRQOXFKhRsT5qVOR3THpYC1hsVLjCAQ"
CHANNEL = "@MaDoSiNPlus"

# ---------- start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام\n\n"
        "🔹 اول عضو کانال شو:\n"
        "https://t.me/MaDoSiNPlus\n\n"
        "🔹 بعد لینک یوتیوب رو بفرست"
    )

# ---------- check join ----------
async def is_member(context, user_id):
    try:
        m = await context.bot.get_chat_member(CHANNEL, user_id)
        return m.status not in ("left", "kicked")
    except:
        return False

# ---------- get link ----------
async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_member(context, update.effective_user.id):
        await update.message.reply_text(
            "❌ اول باید عضو کانال بشی:\nhttps://t.me/MaDoSiNPlus"
        )
        return

    url = update.message.text.strip()
    if "youtu" not in url:
        await update.message.reply_text("❌ لینک یوتیوب معتبر بفرست")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 لینک 720p", callback_data=f"720|{url}")],
        [InlineKeyboardButton("🎧 لینک صدا", callback_data=f"audio|{url}")],
    ])

    await update.message.reply_text(
        "کیفیت رو انتخاب کن 👇",
        reply_markup=keyboard
    )

# ---------- button ----------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quality, url = query.data.split("|", 1)

    if quality == "720":
        text = (
            "🎥 لینک ویدیو (720p):\n\n"
            f"{url}\n\n"
            "⚠️ برای دانلود واقعی، ربات باید روی VPS اجرا شود."
        )
    else:
        text = (
            "🎧 لینک صدا:\n\n"
            f"{url}\n\n"
            "⚠️ برای دانلود واقعی، ربات باید روی VPS اجرا شود."
        )

    await query.edit_message_text(text)

# ---------- run ----------
def main():
    print("BOT RUNNING (SAFE MODE)")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_link))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()

if __name__ == "__main__":
    main()
