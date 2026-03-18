import os
import requests
import sqlite3
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# 💾 DATABASE (PERMANENT MEMORY)
conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    birthday TEXT
)
""")
conn.commit()

def save_user(user_id, name=None, birthday=None):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    if name:
        cursor.execute("UPDATE users SET name=? WHERE user_id=?", (name, user_id))
    if birthday:
        cursor.execute("UPDATE users SET birthday=? WHERE user_id=?", (birthday, user_id))
    conn.commit()

def get_user(user_id):
    cursor.execute("SELECT name, birthday FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

# 🧠 MULTI AI BRAIN
def ai_reply(user_id, text):
    name, birthday = (None, None)
    user = get_user(user_id)
    if user:
        name, birthday = user

    system_prompt = "You are a smart, friendly AI assistant."
    if name:
        system_prompt += f" User name is {name}."
    if birthday:
        system_prompt += f" Important date: {birthday}."

    # 1️⃣ TRY OPENROUTER
    if OPENROUTER_API_KEY:
        try:
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ]
                }
            ).json()

            return res["choices"][0]["message"]["content"]
        except:
            pass

    # 2️⃣ FALLBACK (SMART RESPONSE)
    return "🤖 I’m thinking… try again or rephrase."

# 🎤 REAL VOICE → TEXT (FREE TELEGRAM FILE + SIMPLE TRANSCRIPTION PLACEHOLDER)
def voice_to_text(file_id):
    file_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
    file_path = file_info["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

    # download voice file
    audio = requests.get(file_url)

    # ⚠️ TRUE AI VOICE NEEDS API (next upgrade)
    return "🎤 Voice received (upgrade coming for full speech recognition)"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    if "message" in data:
        msg = data["message"]
        chat_id = str(msg["chat"]["id"])

        # 🎤 VOICE
        if "voice" in msg:
            text = voice_to_text(msg["voice"]["file_id"])
        else:
            text = msg.get("text", "").strip().lower()

        # 💾 MEMORY COMMANDS
        if "my name is" in text:
            name = text.split("my name is")[-1].strip()
            save_user(chat_id, name=name)
            reply = f"Nice to meet you {name} 👋"

        elif "what is my name" in text:
            user = get_user(chat_id)
            reply = f"Your name is {user[0]}" if user and user[0] else "I don’t know yet 😢"

        elif "birthday" in text:
            save_user(chat_id, birthday=text)
            reply = "🎂 Saved your birthday!"

        elif "when is my birthday" in text:
            user = get_user(chat_id)
            reply = user[1] if user and user[1] else "I don’t know yet 😢"

        else:
            reply = ai_reply(chat_id, text)

        # 📤 SEND
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )

    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
