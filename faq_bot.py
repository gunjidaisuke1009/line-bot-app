import gspread
from oauth2client.service_account import ServiceAccountCredentials
from openai import OpenAI

# Google認証
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    r"C:\Users\軍司大輔\OneDrive\ドキュメント\linefaqbot-e5d368ff1a22.json", scope)
client = gspread.authorize(creds)

# スプレッドシートを開く
sheet = client.open("FAQ　よくある質問＆回答").sheet1
records = sheet.get_all_records()

# 質問リスト
faq_questions = [r['質問'] for r in records if r['質問']]

# OpenAIのクライアント
client_ai = OpenAI(api_key="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")

def find_best_faq(user_input, faq_questions):
    messages = [
        {"role": "system", "content": "あなたはFAQシステムです。ユーザーの質問に最も近い既存のFAQ質問を選び、日本語でその質問文だけを返してください。"},
        {"role": "user", "content": f"以下の候補から、ユーザーの質問に最も近いものを1つ日本語で返答してください。\n候補: {faq_questions}\nユーザーの質問: {user_input}"}
    ]
    response = client_ai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    print("GPTの生返答:", response.choices[0].message.content.strip())
    return response.choices[0].message.content.strip()

while True:
    user_input = input("質問を入力してください（qで終了）: ")
    if user_input.lower() == "q":
        break

    matched_question = find_best_faq(user_input, faq_questions)

    # 部分一致検索 (GPTの返答にスプレッドシート側の質問が含まれているか)
    answer = next((r['回答'] for r in records if r['質問'] in matched_question), None)

    if answer:
        print("回答:", answer)
    else:
        print("回答: ごめんなさい、該当する回答が見つかりませんでした。")
