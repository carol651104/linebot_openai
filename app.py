from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 👉 計數器（全域變數）
counter = 0

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global counter
    text1 = event.message.text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-5-nano",
            temperature=0.7,
            messages=[
                # 👉 System Prompt（人格 + 語言控制）
                {
                    "role": "system",
                    "content": "你是一位溫柔、理性且樂於助人的AI助理。請一律使用繁體中文回答，語氣親切、清晰、有條理，並且能夠回答各種類型的問題。"
                },
                {
                    "role": "user",
                    "content": text1
                }
            ]
        )

        ret = response['choices'][0]['message']['content'].strip()

        # 👉 計數 +1
        counter += 1

        # 👉 把計數附在回覆中（可選）
        ret += f"\n\n（目前已呼叫 OpenAI 次數：{counter}）"

    except Exception as e:
        print(e)
        ret = '發生錯誤！'

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=ret)
    )

if __name__ == '__main__':
    app.run()
