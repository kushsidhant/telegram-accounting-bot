import os
import json
import re
import gspread
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")

credentials_dict = json.loads(GOOGLE_CREDENTIALS)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    credentials_dict, scope
)

client = gspread.authorize(creds)
sheet = client.open("Bhartiyavibes Orders").sheet1

def parse_order(text):
    text = text.lower()
    numbers = re.findall(r"\d+", text)
    order_id = numbers[0] if numbers else ""
    amount = numbers[-1] if len(numbers) > 1 else ""
    status = "Pending"

    if "dispatched" in text or "भेज" in text:
        status = "Dispatched"
    elif "paid" in text or "भुगतान" in text:
        status = "Paid"

    name = re.sub(r"\d+|dispatched|paid|pending|order|amount", "", text).strip().title()

    return order_id, name, amount, status

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    order_id, name, amount, status = parse_order(text)

    if not order_id or not amount:
        await update.message.reply_text("Order ID ya Amount detect nahi hua.")
        return

    date = datetime.now().strftime("%Y-%m-%d")
    sheet.append_row([date, order_id, name, amount, status])
    await update.message.reply_text("✅ Order Added!")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def home():
    return "Bot is running"

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    app.update_queue.put_nowait(update)
    return "OK"

if __name__ == "__main__":
    app.bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
