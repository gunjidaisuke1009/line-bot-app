from flask import Flask, request, abort
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest

from google.oauth2 import service_account
from googleapiclient.discovery import build
from difflib import get_close_matches
import openai
import json

app = Flask(__name__)

# 設定
LINE_CHANNEL_ACCESS_TOKEN = 'jzqycybsSHMfW87LshlhTfB+I+XOErsh9cyA5jplM6kEu0V1KbHDofwgKT+Lm4/PTENVqbM+J3XO6NMwHeu2d2ZCWJwasv2duJOcm5cdxrDb8G8g9cGSvvhJKTaVVcSH+zwThs8tIRayTU4fB2hNGgdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '4f6fffc6f1b78dfaf935cb16f4cda131'
openai.api_key = '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'

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# スプレッドシート設定
SPREADSHEET_ID = '1687_Ybu1rMONHsAGutAgf5ItJ_IgmXQZdKydne4OAjM'
RANGE_NAME = 'シート1!B:C'
SERVICE_ACCOUNT_FILE = 'credentials.json'

def get_faq_dict():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    return {row[0]: row[1] for row in values if len(row) >= 2}

@app.route("/callback", methods=['POST'])
def callback():
    print("===== /callback にアクセスあり =====")
    body = request.get_data(as_text=True)
    signature = request.headers.get('X-Line-Signature', '')

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Webhook handling error:", e)
        print("Request body:", body)
        print("Signature:", signature)
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    print(f"=== handle_message 呼ばれた ===\nユーザーからのメッセージ: {user_message}")
    faq_dict = get_faq_dict()

    close_matches = get_close_matches(user_message, faq_dict.keys(), n=1, cutoff=0.6)
    if close_matches:
        response = faq_dict[close_matches[0]]
    else:
        prompt = "以下の質問例の中から、ユーザーの質問に一番近いものを選んで回答してください。\n\n"
        for question, answer in faq_dict.items():
            prompt += f"- {question}: {answer}\n"
        prompt += f"\nユーザーの質問: {user_message}\n\n適切な回答をしてください。"

        gpt_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        response = gpt_response.choices[0].message.content.strip()

    is_question = any(keyword in user_message for keyword in ["？", "?", "か", "ますか", "どこ", "いつ"])
    if not is_question:
        response = "不明な点があればこのチャットでお気軽にご質問ください。\nその他の個別のお問い合わせは〇〇までお願いいたします。"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response)]
            )
        )

if __name__ == "__main__":
    app.run(port=5000)
