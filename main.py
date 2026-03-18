import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")

@app.route("/")
def home():
    return "OK"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("WEBHOOK HIT:", data)

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": f"Echo: {text}"
        }
    )

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
