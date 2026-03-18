import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")

@app.route("/")
def home():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("DATA:", data)

    try:
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

            response = requests.post(url, json={
                "chat_id": chat_id,
                "text": f"Echo: {text}"
            })

            print("TELEGRAM RESPONSE:", response.text)

    except Exception as e:
        print("ERROR:", str(e))

    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
