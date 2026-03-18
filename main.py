import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")

# SEND MESSAGE (WITH DEBUG)
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    res = requests.post(url, json={"chat_id": chat_id, "text": text})
    print("SEND STATUS:", res.text)  # 👈 THIS IS IMPORTANT

@app.route("/")
def home():
    return "MiserBot running 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    print("INCOMING:", data)  # 👈 DEBUG

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]

        # 🔥 FORCE REPLY
        send_message(chat_id, "🔥 MISERBOT IS ALIVE")

    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
