from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# LINEの設定
line_bot_api = LineBotApi('CcnZvdcAjxe9vDqAXxXIDdwn5B9wdMuQf40bQx8RdJRXwRlm8Nv/cvdGoAenrWmXTENVqbM+J3XO6NMwHeu2d2ZCWJwasv2duJOcm5cdxrCU7DJxU8mbS+eAuD/KnwimsgWffhgDGF5U2RwTkoAUAAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('4f6fffc6f1b78dfaf935cb16f4cda131')

# OpenAIの設定
openai.api_key = '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'

# Google Sheets API の設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("linefaqbot-e5d368ff1a22.json", scope)
client = gspread.authorize(creds)
sheet = client.open("FAQ　よくある質問＆回答").sheet1
records = sheet.get_all_records()

@app.route("/")
def hello_world():
    return "Hello from LINE Bot!", 200

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def find_best_faq(user_input):
    faq_questions = [r['質問'] for r in records if r['質問']]
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはFAQサポートBOTです。次のリストからユーザーの質問にもっとも近い質問を1つだけ選び、その質問だけをJSON配列形式で答えてください: " + str(faq_questions)},
            {"role": "user", "content": user_input}
        ]
    )
    matched = completion.choices[0].message['content']
    print("GPTの生返答:", matched)
    return matched.replace('[','').replace(']','').replace('"','').strip()

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    matched_question = find_best_faq(user_input)
    answer = next((r['回答'] for r in records if r['質問'] == matched_question), "ごめんなさい、該当する回答が見つかりませんでした。")
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=answer))

if __name__ == "__main__":
    app.run(port=5000)
