import logging
import os

from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ================== ENV ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL is not set")

ADMIN_ID = 7793192501

# ================== Mongo ==================

client = MongoClient(MONGO_URL)

# ================== Logging ==================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

user_payments = {}

# ================== Handlers ==================

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

# ================== Main ==================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment))
    app.add_handler(CallbackQueryHandler(review_action))

    print("🤖 Review Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
