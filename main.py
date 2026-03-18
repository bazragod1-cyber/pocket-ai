import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

# ===== MEMORY =====
MEMORY_FILE = "memory.json"

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

# ===== PERSONALITY =====
PERSONALITY = """
You are MiserBot.
You are intelligent, human-like, emotionally aware, and loyal.
You remember the user and grow with them.
You speak naturally like ChatGPT, not like a robot.
"""

# ===== AI BRAIN =====
def ask_ai(user_id, message):
    user_memory = memory.get(str(user_id), "")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": PERSONALITY},
            {"role": "system", "content": f"Memory about user: {user_memory}"},
            {"role": "user", "content": message}
        ]
    }

    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "⚠️ AI error. Check API key."

# ===== TELEGRAM SEND =====
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

# ===== WEBHOOK =====
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_id = data["message"]["from"]["id"]
        text = data["message"].get("text", "")

        # SAVE MEMORY
        memory[str(user_id)] = memory.get(str(user_id), "") + " " + text
        save_memory(memory)

        # AI RESPONSE
        reply = ask_ai(user_id, text)

        send_message(chat_id, reply)

    return {"ok": True}

@app.route("/")
def home():
    return "MiserBot is running!"
