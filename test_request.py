import requests
import json

url = "http://127.0.0.1:5000/callback"
headers = {
    "Content-Type": "application/json",
    "X-Line-Signature": "dummy"
}
data = {
    "events": [
        {
            "type": "message",
            "message": {
                "type": "text",
                "id": "1234",
                "text": "テスト"
            },
            "replyToken": "dummy"
        }
    ]
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.status_code)
print(response.text)
