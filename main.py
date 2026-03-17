import os
import time
import requests
from openai import OpenAI
import anthropic

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
XAI_API_KEY = os.getenv("XAI_API_KEY")

def duck_search(query):
    try:
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json"}
        res = requests.get(url, params=params)
        data = res.json()

        if data.get("AbstractText"):
            return data["AbstractText"]
        return "No result found."

    except Exception as e:
        return f"Search error: {e}"

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

def ask_grok(prompt):
    try:
        import requests
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {XAI_API_KEY}",
            "Content-Type": "application/json"
        }
        json_data = {
            "model": "grok-beta",
            "messages": [{"role": "user", "content": prompt}]
        }
        res = requests.post(url, headers=headers, json=json_data)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Grok error: {e}"

def smart_ai(prompt):
    while True:
        try:
            return ask_openai(prompt)
        except:
            try:
                return ask_anthropic(prompt)
            except:
                try:
                    return ask_grok(prompt)
                except:
                    time.sleep(10)

def main():
    print("Bot running...")

    while True:
        try:
            user_input = input("You: ")

            if user_input.startswith("search "):
                print(duck_search(user_input.replace("search ", "")))
                continue

            reply = smart_ai(user_input)
            print("Bot:", reply)

        except Exception as e:
            print("Error:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
