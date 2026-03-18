import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# 🧠 FREE AI (DuckDuckGo Instant Answer)
def free_ai_reply(user_text):
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": user_text,
            "format": "json"
        }

        res = requests.get(url, params=params).json()

        # Try direct answer
        if res.get("AbstractText"):
            return res["AbstractText"]

        # Try related topics
        if res.get("RelatedTopics"):
            for topic in res["RelatedTopics"]:
                if isinstance(topic, dict) and topic.get("Text"):
                    return topic["Text"]

        return "🤖 I couldn't find a clear answer, but I'm learning!"

    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # 🧠 GET FREE AI RESPONSE
        reply = free_ai_reply(text)

        # 📤 SEND TO TELEGRAM
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": reply
        })

    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
