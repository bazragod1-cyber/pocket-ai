import os
import requests
import json
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

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

# 🧠 AI BRAIN (OpenRouter)
def ai_reply(user_id, text):
    if not OPENROUTER_API_KEY:
        return "⚠️ AI key missing"

    # ensure user memory exists
    if user_id not in memory:
        memory[user_id] = {}

    user_data = memory[user_id]

    # build context
    system_prompt = "You are a smart, friendly, slightly funny AI assistant."

    # include memory if exists
    if "name" in user_data:
        system_prompt += f" The user's name is {user_data['name']}."
    if "birthday" in user_data:
        system_prompt += f" Their important date: {user_data['birthday']}."

    try:
        response = requests.post(
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
        )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {str(e)}"

# 🎤 HANDLE VOICE (basic placeholder)
def handle_voice(file_id):
    return "🎤 I got your voice message! (voice AI coming next)"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]

        # 🎤 voice message
        if "voice" in msg:
            reply = handle_voice(msg["voice"]["file_id"])

        else:
            text = msg.get("text", "").strip().lower()

            # 🧠 MEMORY COMMANDS
            if "my name is" in text:
                name = text.split("my name is")[-1].strip()
                memory[chat_id] = memory.get(chat_id, {})
                memory[chat_id]["name"] = name
                save_memory(memory)
                reply = f"Nice to meet you {name} 👋"

            elif "what is my name" in text:
                name = memory.get(chat_id, {}).get("name", None)
                reply = f"Your name is {name}" if name else "I don’t know yet 😢"

            elif "birthday" in text:
                memory[chat_id] = memory.get(chat_id, {})
                memory[chat_id]["birthday"] = text
                save_memory(memory)
                reply = "🎂 Got it! I’ll remember that."

            elif "when is my birthday" in text:
                bday = memory.get(chat_id, {}).get("birthday", None)
                reply = bday if bday else "I don’t know yet 😢"

            else:
                # 🧠 AI RESPONSE
                reply = ai_reply(chat_id, text)

        # 📤 SEND MESSAGE
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": reply
        })

    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
