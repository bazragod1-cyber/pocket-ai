def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)
