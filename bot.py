import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from datetime import datetime

# Get token & credentials from environment
TOKEN = os.environ.get("BOT_TOKEN")
credentials_json = os.environ.get("GOOGLE_CREDENTIALS")

credentials_dict = json.loads(credentials_json)

SHEET_NAME = "Bhartiyavibes Orders"

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    credentials_dict, scope
)

client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    parts = text.split(",")

    if len(parts) < 4:
        await update.message.reply_text("Format: OrderID, Name, Amount, Status")
        return

    date = datetime.now().strftime("%Y-%m-%d")

    sheet.append_row([
        date,
        parts[0].strip(),
        parts[1].strip(),
        parts[2].strip(),
        parts[3].strip()
    ])

    await update.message.reply_text("✅ Order Added Successfully!")


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()
