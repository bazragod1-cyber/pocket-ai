import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROK_API_KEY = os.environ.get("GROK_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        reply = "⚠️ No AI response yet"

        # 🧠 TRY GROK AI
        if GROK_API_KEY:
            try:
                headers = {
                    "Authorization": f"Bearer {GROK_API_KEY}",
                    "Content-Type": "application/json"
                }

                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": "grok-1",
                        "messages": [
                            {"role": "system", "content": "You are a smart, helpful assistant."},
                            {"role": "user", "content": text}
                        ]
                    }
                )

                result = response.json()
                reply = result["choices"][0]["message"]["content"]

            except Exception as e:
                reply = f"Error: {str(e)}"

        else:
            reply = f"🤖 You said: {text}"

        # 📤 SEND TO TELEGRAM
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": reply
        })

    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
