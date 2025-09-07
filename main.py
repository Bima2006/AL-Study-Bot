import os
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# API Keys
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi! I'm your A/L Study Bot.\nSend me any Maths, Physics, Chemistry, or Biology question as text, photo, or file 📚.")

# Text questions
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert A/L teacher for Maths, Physics, Chemistry, and Biology."},
            {"role": "user", "content": user_input}
        ]
    )

    answer = response.choices[0].message.content
    await update.message.reply_text(answer)

# Photo questions
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file()
    file_path = "question.jpg"
    await file.download_to_drive(file_path)

    text = pytesseract.image_to_string(Image.open(file_path))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert A/L teacher for Maths, Physics, Chemistry, and Biology."},
            {"role": "user", "content": text}
        ]
    )

    answer = response.choices[0].message.content
    await update.message.reply_text(answer)

# File questions (PDF, DOCX, TXT)
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_path = "question.pdf"
    await file.download_to_drive(file_path)

    # For now, just tell user we only support images + text. (Later add PDF parsing)
    await update.message.reply_text("Currently I support text & images. PDF support coming soon 📄.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    app.run_polling()

if __name__ == "__main__":
    main()
