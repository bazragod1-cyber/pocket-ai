import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# 🧠 MEMORY STORE (simple)
memory = {}

def free_search(query):
    try:
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json"}
        res = requests.get(url, params=params).json()

        if res.get("AbstractText"):
            return res["AbstractText"]

        if res.get("RelatedTopics"):
            for topic in res["RelatedTopics"]:
                if isinstance(topic, dict) and topic.get("Text"):
                    return topic["Text"]

    except:
        pass

    return None

def smart_reply(user_id, text):
    text_lower = text.lower()

    # 🧠 MEMORY RECALL
    if "my name is" in text_lower:
        name = text.split("my name is")[-1].strip()
        memory[user_id] = {"name": name}
        return f"Nice to meet you, {name}! I'll remember that."

    if user_id in memory and "what is my name" in text_lower:
        return f"Your name is {memory[user_id]['name']} 😎"

    # 💬 BASIC CONVERSATION
    if "father" in text_lower:
        return "😂 I'm not your father... but I can be your AI assistant."

    if text_lower in ["hi", "hello"]:
        return "Hey 👋 I'm your AI bot. Ask me anything!"

    # 🌐 SEARCH FALLBACK
    search = free_search(text)
    if search:
        return search

    return "🤖 I'm still learning, but try asking me something else!"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        reply = smart_reply(chat_id, text)

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": reply
        })

    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
