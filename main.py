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
    birthday TEXT
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

# 💾 USER MEMORY
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

# 💬 CHAT MEMORY
def save_message(user_id, role, content):
    cursor.execute("INSERT INTO messages VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()

def get_history(user_id):
    cursor.execute("SELECT role, content FROM messages WHERE user_id=? ORDER BY ROWID DESC LIMIT 6", (user_id,))
    rows = cursor.fetchall()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

# 🧠 AI BRAIN
def ai_reply(user_id, text):
    history = get_history(user_id)

    name, birthday = (None, None)
    user = get_user(user_id)
    if user:
        name, birthday = user

    system_prompt = "You are MiserBot, a smart, powerful, slightly confident AI assistant."

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

        # save conversation
        save_message(user_id, "user", text)
        save_message(user_id, "assistant", reply)

        return reply

    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/", methods=["GET"])
def home():
    return "MiserBot is alive 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    if "message" in data:
        msg = data["message"]
        chat_id = str(msg["chat"]["id"])
        text = msg.get("text", "").strip().lower()

        if "my name is" in text:
            name = text.split("my name is")[-1].strip()
            save_user(chat_id, name=name)
            reply = f"Got it. {name}, I won’t forget."

        elif "birthday" in text:
            save_user(chat_id, birthday=text)
            reply = "Saved. I’ll remember that date."

        else:
            reply = ai_reply(chat_id, text)

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )

    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
