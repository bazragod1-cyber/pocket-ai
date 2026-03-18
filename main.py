from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

@app.route("/")
def home():
    return "MiserBot running 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            reply = f"You said: {text}"

            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": reply
            })

        return "ok", 200

    except Exception as e:
        print("ERROR:", e)
        return "error", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
