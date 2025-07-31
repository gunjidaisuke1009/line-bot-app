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

# Drive上のスプレッドシート一覧を取得
files = client.list_spreadsheet_files()
for file in files:
    print(file['name'])
