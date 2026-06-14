from telegram.ext import ContextTypes     
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup                                        
import os
import json
import google_sheets_api as gs
import genai_api as ai
from datetime import datetime


ALLOWED_GROUPS = [-5031634171, -1003923716298]

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

    current_photo_message_id = update.message.message_id

    try:
        ai_raw_json = await ai.analyze_receipt_with_ai(local_path)
        print(f"AI extracted data: {ai_raw_json}")
        data = json.loads(ai_raw_json)

        if not data.get("is_receipt", False):
            print(f"Quality Gate: Image in message {current_photo_message_id} is not a receipt.")

            await update.message.reply_text(
                text="Di naman are resibo nganii!",
                reply_to_message_id=current_photo_message_id
            )
            return

        gs.sheet = gs.connect_to_google_sheet("Expense Tracker")
        gs.append_receipt_to_sheet(
            gs.sheet,
            id=current_photo_message_id,
            merchant=data["merchant"],
            total_amount=data["total_amount"],
            date=data["transaction_date"],
            category=data["category"],
            logged_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        keyboard = [
            [
                InlineKeyboardButton("Delete", callback_data=f"delete_row:{current_photo_message_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)


        await update.message.reply_text(
            text=f"Recorded successfully! \nStore: {data['merchant']}\nTotal: ₱{data['total_amount']:.2f}\nDate: {data['transaction_date']}\nCategory: {data['category']}",
            reply_to_message_id=current_photo_message_id,
            reply_markup=reply_markup
        )

    except Exception as e:
        print(f"Error during execution: {e}")
        await update.message.reply_text(
            text="Sorry, I ran into an error trying to process this image.",
            reply_to_message_id=current_photo_message_id
        )
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
            print("Cleaned up local staging file.")


async def handle_deletion_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data_parts = query.data.split(":")
    target_message_id = data_parts[1]

    chat_id = query.message.chat_id
    bot_reply_message_id = query.message.message_id

    try:
        sheet = gs.connect_to_google_sheet("Expense Tracker")
        all_rows = sheet.get_all_values()
        row_to_delete = None

        for index, row in enumerate(all_rows):
            if row and str(row[0]).strip() == str(target_message_id).strip():
                row_to_delete = index + 1
                break

        if row_to_delete:
            sheet.delete_rows(row_to_delete)
            print(f"Successfully deleted sheet row {row_to_delete} linked to message {target_message_id}")
            
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=target_message_id)
            except Exception as e:
                print(f"Could not delete original photo (might already be deleted): {e}")

            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=bot_reply_message_id)
            except Exception as e:
                print(f"Could not delete bot reply message: {e}")
        else:
            await query.edit_message_text(text="This entry has already been removed from the database")

    except Exception as e:
        print(f"Failed to execute callback deletion pipeline: {e}")