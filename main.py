import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
print("TOKEN LOADED:", TOKEN)

SEND_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

@app.route("/")
def home():
    return "Bot is alive"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("INCOMING DATA:", data)

    try:
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            reply = f"🔥 You said: {text}"

            response = requests.post(SEND_URL, json={
                "chat_id": chat_id,
                "text": reply
            })

            print("TELEGRAM RESPONSE:", response.text)

    except Exception as e:
        print("ERROR:", str(e))

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
