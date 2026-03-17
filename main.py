import os
from flask import Flask, request
import requests
from openai import OpenAI
import anthropic

app = Flask(__name__)

# ========================
# API KEYS
# ========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ========================
# MEMORY
# ========================

memory = {}

def update_memory(user_id, message):
    if user_id not in memory:
        memory[user_id] = []
    memory[user_id].append(message)
    memory[user_id] = memory[user_id][-10:]

def get_memory_context(user_id):
    return "\n".join(memory.get(user_id, []))

# ========================
# AI
# ========================

def ask_openai(prompt):
    response = openai_client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text

def ask_anthropic(prompt):
    msg = anthropic_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text

def smart_ai(prompt, user_id):
    context = get_memory_context(user_id)

    full_prompt = f"""
Conversation:
{context}

User: {prompt}
"""

    if len(prompt) < 50:
        return ask_anthropic(full_prompt)
    return ask_openai(full_prompt)

# ========================
# TELEGRAM SEND
# ========================

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

# ========================
# WEBHOOK ROUTE
# ========================

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        update_memory(chat_id, text)

        reply = smart_ai(text, chat_id)

        update_memory(chat_id, reply)

        send_message(chat_id, reply)

    return "ok"

# ========================
# START SERVER
# ========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
