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
You speak naturally like ChatGPT, not robotic.
"""

# ===== AI =====
def ask_ai(user_id, message):
    user_memory = memory.get(str(user_id), "")

    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": PERSONALITY},
                    {"role": "system", "content": f"Memory: {user_memory}"},
                    {"role": "user", "content": message}
                ]
            }
        )
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "⚠️ AI error (check API key)"

# ===== SEND MESSAGE =====
def send_message(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

# ===== ROUTES =====
@app.route("/", methods=["GET"])
def home():
    return "MiserBot running 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_id = data["message"]["from"]["id"]
        text = data["message"].get("text", "")

        # save memory
        memory[str(user_id)] = memory.get(str(user_id), "") + " " + text
        save_memory(memory)

        # AI reply
        reply = ask_ai(user_id, text)

        send_message(chat_id, reply)

    return {"ok": True}

# ===== FIX (SERVER STARTS HERE) =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
