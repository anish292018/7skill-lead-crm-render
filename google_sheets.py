import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def setup_google_sheets():
    try:
        creds_json = os.getenv("GSHEET_CREDENTIALS")
        sheet_id = os.getenv("GSHEET_ID")

        if not creds_json or not sheet_id:
            print("❌ Missing Google Sheets ENV variables")
            return None

        creds_dict = json.loads(creds_json)

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict, scope
        )

        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).sheet1
        return sheet

    except Exception as e:
        print(f"Google Sheets error: {e}")
        return None

