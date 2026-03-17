import os
import time
import requests
from openai import OpenAI
import anthropic

# ========================
# API KEYS
# ========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ========================
# TELEGRAM
# ========================

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    return requests.get(url, params=params).json()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

# ========================
# AI FUNCTIONS
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

# ========================
# SMART ROUTER
# ========================

def smart_ai(prompt):
    try:
        if len(prompt) < 50:
            return ask_anthropic(prompt)
        return ask_openai(prompt)
    except:
        return ask_openai(prompt)

# ========================
# MAIN TELEGRAM LOOP
# ========================

def main():
    print("🤖 Telegram AI Bot Running...")
    offset = None

    while True:
        try:
            updates = get_updates(offset)

            for update in updates["result"]:
                offset = update["update_id"] + 1

                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"].get("text", "")

                    print("User:", text)

                    reply = smart_ai(text)

                    send_message(chat_id, reply)

            time.sleep(2)

        except Exception as e:
            print("Error:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
