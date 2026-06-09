from telegram.ext import ContextTypes     
from telegram import Update                                           
import os
import json
import google_sheets_api as gs
import genai_api as ai
from datetime import datetime


ALLOWED_GROUPS = [-5031634171]

async def handle_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_chat_id = update.effective_chat.id
    print(f"Group chat id: {update.effective_chat.id}")
    if current_chat_id not in ALLOWED_GROUPS:
        print(f"Unauthorized access attempt by: {current_chat_id}")

        await update.message.reply_text("You are not authorized to use this bot! Shoo!")
        return
    
    print("Received a photo!")
    photo = update.message.photo[-1]
   
    file = await context.bot.get_file(photo.file_id)
    os.makedirs("./staging", exist_ok=True)
    local_path = f"./staging/{photo.file_id}.jpg"
    await file.download_to_drive(local_path)
    print(f"Successfully downloaded receipt to: {local_path}")

    try:
        ai_raw_json = await ai.analyze_receipt_with_ai(local_path)
        current_photo_message_id = update.message.message_id
        print(f"AI extracted data: {ai_raw_json}")
        data = json.loads(ai_raw_json)

        if not data.get("is_receipt", False):
            print(f"Quality Gate: Image in message {current_photo_message_id} is not a receipt.")

            await update.message.reply_text(
                text="Di naman are resibo nganii!",
                reply_to_message_id=current_photo_message_id
            )
            os.remove(local_path)
            return

        gs.sheet = gs.connect_to_google_sheet("Expense Tracker")
        gs.append_receipt_to_sheet(
            gs.sheet,
            merchant=data["merchant"],
            total_amount=data["total_amount"],
            date=data["transaction_date"],
            category=data["category"],
            logged_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        os.remove(local_path)
        print("Cleaned up local staging file.")

        await update.message.reply_text(
            text=f"Recorded successfully! \nStore: {data['merchant']}\nTotal: ₱{data['total_amount']:.2f}\nDate: {data['transaction_date']}\nCategory: {data['category']}",
            reply_to_message_id=current_photo_message_id
        )
    except Exception as e:
        print(f"Error during execution: {e}")
        await update.message.reply_text(
            text="Sorry, I ran into an error tyring to process this image.",
            reply_to_message_id=current_photo_message_id
        )