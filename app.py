from telegram.ext import ApplicationBuilder, MessageHandler, filters                               
import os
import telegram_bot_api as tg


def main():

    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    photo_handler = MessageHandler(filters.PHOTO, tg.handle_receipt_photo)
    application.add_handler(photo_handler)

    print("Bot is listening for receipts...")
    application.run_polling()

if __name__ == '__main__':
    main()