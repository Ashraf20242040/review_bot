import logging
import os

from dotenv import load_dotenv
load_dotenv()   # 👈 دا باید تر MongoClient مخکې وي

from pymongo import MongoClient

mongo_url = os.getenv("MONGO_URL")
if not mongo_url:
    raise RuntimeError("MONGO_URL is not set")

client = MongoClient(mongo_url)


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================== تنظیمات ==================
BOT_TOKEN = "8004049260:AAEHM2Yop8qTBtzS3qJ6oqJ7gsbLoshLrAA"
ADMIN_ID = 7793192501
# ============================================

user_payments = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام!\n"
        "مهرباني وکړئ د تادیې معلومات ولیږئ."
    )

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_payments[user.id] = update.message.text

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
    ]])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"👤 {user.full_name}\n🆔 {user.id}\n\n{update.message.text}",
        reply_markup=keyboard
    )

    await update.message.reply_text("⏳ ستاسو تادیه تر ارزونې لاندې ده.")

async def review_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    action, user_id = query.data.split("_")
    user_id = int(user_id)

    if action == "approve":
        await context.bot.send_message(user_id, "✅ ستاسو تادیه تایید شوه.")
        await query.edit_message_text("✅ Approved")
    else:
        await context.bot.send_message(user_id, "❌ ستاسو تادیه رد شوه.")
        await query.edit_message_text("❌ Rejected")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment))
    app.add_handler(CallbackQueryHandler(review_action))

    print("✅ Review Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("🤖 Bot is running...")
    app.run_polling()
