import requests
import time
import os

TOKEN = os.getenv("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

last_update_id = None

def get_updates():
    global last_update_id
    params = {"timeout": 30}

    if last_update_id:
        params["offset"] = last_update_id + 1

    response = requests.get(f"{URL}/getUpdates", params=params)
    data = response.json()

    return data.get("result", [])

def send_message(chat_id, text):
    response = requests.post(f"{URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })
    print("SEND RESPONSE:", response.text)

def handle_update(update):
    global last_update_id

    last_update_id = update["update_id"]

    if "message" not in update:
        return

    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "")

    print("RECEIVED:", text)

    send_message(chat_id, f"🔥 Miserbot: {text}")

def main():
    print("🤖 Miserbot is running...")

    while True:
        updates = get_updates()

        for update in updates:
            handle_update(update)

        time.sleep(1)

if __name__ == "__main__":
    main()
