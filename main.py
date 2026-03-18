@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("WEBHOOK HIT:", data)

    try:
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "No text received")

        if chat_id:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": f"Echo: {text}"
                }
            )

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200
