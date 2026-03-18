import os
import requests
from flask import Flask, request

app = Flask(__name__)

# 🔑 TOKENS
TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

# 📤 SEND MESSAGE
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

# 🧠 AI FUNCTION
def ask_ai(message):
    if not OPENROUTER_KEY:
        return "⚠️ No AI key set, but I’m alive!"

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are MiserBot, a smart helpful assistant."},
                    {"role": "user", "content": message}
                ]
            }
        )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except:
        return "⚠️ AI error, but I’m still working!"

# 🌐 HOME ROUTE
@app.route("/", methods=["GET"])
def home():
    return "MiserBot running 🚀"

# 📩 TELEGRAM WEBHOOK
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # 🧠 GET REPLY
        reply = ask_ai(text)

        # 📤 SEND BACK
        send_message(chat_id, reply)

    return {"ok": True}

# 🚀 START SERVER (VERY IMPORTANT)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
