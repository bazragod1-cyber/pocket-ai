import os
import requests
import json
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

MEMORY_FILE = "memory.json"

# 📂 LOAD MEMORY
def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

memory = load_memory()

# 🌐 SEARCH
def search(query):
    try:
        url = "https://api.duckduckgo.com/"
        res = requests.get(url, params={"q": query, "format": "json"}).json()

        if res.get("AbstractText"):
            return res["AbstractText"]

        if res.get("RelatedTopics"):
            for t in res["RelatedTopics"]:
                if isinstance(t, dict) and t.get("Text"):
                    return t["Text"]
    except:
        pass
    return None

# 🧠 SMART CHAT
def brain(user_id, text):
    text_lower = text.lower()

    if user_id not in memory:
        memory[user_id] = {}

    user_data = memory[user_id]

    # 🎂 SAVE BIRTHDAY
    if "birthday" in text_lower:
        user_data["birthday"] = text
        save_memory(memory)
        return "🎂 Got it! I’ll remember that birthday."

    if "when is my birthday" in text_lower:
        return user_data.get("birthday", "I don’t know yet 😢")

    # 🧑 NAME MEMORY
    if "my name is" in text_lower:
        name = text.split("my name is")[-1].strip()
        user_data["name"] = name
        save_memory(memory)
        return f"Nice to meet you {name} 👋"

    if "what is my name" in text_lower:
        return f"Your name is {user_data.get('name', 'I don’t know yet')}"

    # 💬 CONVERSATION STYLE
    if "father" in text_lower:
        return "😂 I'm not your father… but I got you."

    if text_lower in ["hi", "hello"]:
        return "Hey 👋 I’m your AI assistant. Talk to me."

    # 🌐 SEARCH FALLBACK
    result = search(text)
    if result:
        return result

    return "🤖 I’m thinking... try asking differently."

# 🎤 GET VOICE FILE TEXT (basic)
def handle_voice(file_id):
    file_url = f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}"
    file_info = requests.get(file_url).json()

    file_path = file_info["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

    # NOTE: real speech-to-text needs API, this is placeholder
    return "🎤 I got your voice message (voice AI upgrade coming soon)"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]

        # 🎤 VOICE MESSAGE
        if "voice" in msg:
            reply = handle_voice(msg["voice"]["file_id"])

        else:
            text = msg.get("text", "")
            reply = brain(chat_id, text)

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": reply
        })

    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
