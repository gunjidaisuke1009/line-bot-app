import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    r"C:\Users\軍司大輔\OneDrive\ドキュメント\linefaqbot-e5d368ff1a22.json", 
    scope
)
client = gspread.authorize(creds)

# ✅ この部分を list_files.py に出た名前に完全一致させる
sheet = client.open("FAQ　よくある質問＆回答").sheet1

records = sheet.get_all_records()
print(records)
