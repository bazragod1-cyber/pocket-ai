import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route("/", methods=["GET"])
def home():
    return "Bot is alive"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    print("Incoming:", data)  # shows in logs

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        reply = f"You said: {text}"

        send_message(chat_id, reply)

    return "ok"

def send_message(chat_id, text):
    requests.post(f"{URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
