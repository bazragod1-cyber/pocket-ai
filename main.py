import os
import requests
import sqlite3
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# 💾 DATABASE
conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    birthday TEXT,
    mode TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    user_id TEXT,
    role TEXT,
    content TEXT
)
""")
conn.commit()

# 💾 USER DATA
def get_user(user_id):
    cursor.execute("SELECT name, birthday, mode FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def update_user(user_id, name=None, birthday=None, mode=None):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    if name:
        cursor.execute("UPDATE users SET name=? WHERE user_id=?", (name, user_id))
    if birthday:
        cursor.execute("UPDATE users SET birthday=? WHERE user_id=?", (birthday, user_id))
    if mode:
        cursor.execute("UPDATE users SET mode=? WHERE user_id=?", (mode, user_id))
    conn.commit()

# 💬 CHAT MEMORY
def save_message(user_id, role, content):
    cursor.execute("INSERT INTO messages VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()

def get_history(user_id):
    cursor.execute("SELECT role, content FROM messages WHERE user_id=? ORDER BY ROWID DESC LIMIT 6", (user_id,))
    rows = cursor.fetchall()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

def reset_memory(user_id):
    cursor.execute("DELETE FROM messages WHERE user_id=?", (user_id,))
    conn.commit()

# 🧠 AI BRAIN
def ai_reply(user_id, text):
    history = get_history(user_id)
    user = get_user(user_id)

    name, birthday, mode = (None, None, "smart")
    if user:
        name, birthday, mode = user

    personality = {
        "smart": "You are MiserBot, a highly intelligent assistant.",
        "funny": "You are MiserBot, funny, sarcastic, and entertaining.",
        "hacker": "You are MiserBot, a hacker-style AI, sharp and bold."
    }

    system_prompt = personality.get(mode, personality["smart"])

    if name:
        system_prompt += f" User name is {name}."
    if birthday:
        system_prompt += f" Important date: {birthday}."

    messages = [{"role": "system", "content": system_prompt}] + history
    messages.append({"role": "user", "content": text})

    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": messages
            }
        ).json()

        reply = res["choices"][0]["message"]["content"]

        save_message(user_id, "user", text)
        save_message(user_id, "assistant", reply)

        return reply

    except Exception as e:
        return f"Error: {str(e)}"

# 🎤 VOICE DOWNLOAD
def get_voice_file(file_id):
    file_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
    file_path = file_info["result"]["file_path"]
    return f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

@app.route("/", methods=["GET"])
def home():
    return "MiserBot V2 Running 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    if "message" in data:
        msg = data["message"]
        chat_id = str(msg["chat"]["id"])

        # 🎤 VOICE
        if "voice" in msg:
            voice_url = get_voice_file(msg["voice"]["file_id"])
            reply = "🎤 Voice received! (Full AI voice next upgrade)"

        else:
            text = msg.get("text", "").strip().lower()

            # COMMANDS
            if text == "/start":
                reply = "👋 Welcome to MiserBot"

            elif text == "/help":
                reply = "/mode smart | /mode funny | /mode hacker | /reset"

            elif text == "/reset":
                reset_memory(chat_id)
                reply = "🔄 Memory cleared"

            elif text.startswith("/mode"):
                mode = text.split(" ")[-1]
                update_user(chat_id, mode=mode)
                reply = f"Mode set to {mode}"

            elif "my name is" in text:
                name = text.split("my name is")[-1].strip()
                update_user(chat_id, name=name)
                reply = f"Got it {name}"

            elif "birthday" in text:
                update_user(chat_id, birthday=text)
                reply = "🎂 Saved"

            else:
                reply = ai_reply(chat_id, text)

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )

    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
