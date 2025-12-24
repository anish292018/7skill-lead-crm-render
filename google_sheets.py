import os
import json
import gspread
from google.oauth2.service_account import Credentials

def save_to_google_sheet(data):
    try:
        creds_json = os.environ.get("GSHEET_CREDENTIALS")
        sheet_id = os.environ.get("GSHEET_ID")

        if not creds_json or not sheet_id:
            print("❌ Google Sheets ENV missing")
            return

        creds_dict = json.loads(creds_json)

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).sheet1

        sheet.append_row(data)
        print("✅ Lead saved to Google Sheet")

    except Exception as e:
        print("❌ Google Sheets error:", e)



