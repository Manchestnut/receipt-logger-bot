import gspread
from google.oauth2.service_account import Credentials
import os, json
from dotenv import load_dotenv
load_dotenv()


def append_receipt_to_sheet(sheet, id, merchant, total_amount, date, category, logged_at):
    row_data = [merchant, id, total_amount, date, category, logged_at]
    sheet.append_row(row_data)
    print("Row successfully inserted into Google Sheets!")

def connect_to_google_sheet(sheet_name: str):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    raw_creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if not raw_creds_json:
        raise ValueError(
            "Google creds missing"
        )
    
    try: 
        creds_dict = json.loads(raw_creds_json)
        creds = Credentials.from_service_account_info(
            creds_dict, 
            scopes=scopes
        )

    except json.JSONDecoder as e:
        raise ValueError(
            f"Failed to parse GOOGLE_CREDENTIALS_JSON. Error: {e}"
        )

    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet
