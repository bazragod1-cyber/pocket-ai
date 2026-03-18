import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

@app.route("/")
def home():
    return "MiserBot is alive"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    print("DATA RECEIVED:", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        reply = f"🤖 MiserBot: You said -> {text}"

        requests.post(URL, json={
            "chat_id": chat_id,
            "text": reply
        })

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
