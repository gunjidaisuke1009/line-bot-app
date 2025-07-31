from flask import Flask, request, abort
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest

from google.oauth2 import service_account
from googleapiclient.discovery import build
from difflib import get_close_matches
import openai
import os
from dotenv import load_dotenv

# .env を読み込む
load_dotenv()

# 環境変数から設定を取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Flask アプリ起動
app = Flask(__name__)

# LINEのWebhook Handler設定
handler = WebhookHandler(LINE_CHANNEL_SECRET)
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)


@app.route("/callback", methods=['POST'])
def callback():
    # LINEからのリクエストを受け取る
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

    # ここにFAQ検索・ChatGPT応答ロジックを記述（省略可能）
    response_text = f"あなたのメッセージ: {user_message}"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
