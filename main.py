import os
import time
import requests
from openai import OpenAI
import anthropic

# ========================
# API SETUP
# ========================

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
XAI_API_KEY = os.getenv("XAI_API_KEY")

# ========================
# DUCKDUCKGO SEARCH
# ========================

def duck_search(query):
    try:
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json"}
        res = requests.get(url, params=params)
        data = res.json()

        if data.get("AbstractText"):
            return data["AbstractText"]

        return "No useful search result."

    except Exception as e:
        return f"Search error: {e}"

# ========================
# AI PROVIDERS
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


def ask_grok(prompt):
    try:
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

# ========================
# 🧠 INTELLIGENT ROUTER
# ========================

def smart_ai(prompt):

    while True:
        try:

            prompt_lower = prompt.lower()

            # 🔍 SEARCH ROUTE
            if "search" in prompt_lower or "latest" in prompt_lower:
                print("Using search-enhanced AI...")
                search_data = duck_search(prompt)
                return ask_openai(f"Use this info:\n{search_data}\n\nAnswer:\n{prompt}")

            # 💻 CODING ROUTE
            elif any(word in prompt_lower for word in ["code", "bug", "fix", "error"]):
                print("Routing → OpenAI (coding)")
                return ask_openai(prompt)

            # ⚡ FAST ROUTE
            elif len(prompt) < 50:
                print("Routing → Anthropic (fast)")
                return ask_anthropic(prompt)

            # 🧠 DEFAULT
            else:
                print("Routing → OpenAI (default)")
                return ask_openai(prompt)

        except Exception as e:
            print("Primary failed:", e)

            try:
                print("Fallback → Anthropic")
                return ask_anthropic(prompt)
            except:
                try:
                    print("Fallback → Grok")
                    return ask_grok(prompt)
                except:
                    print("All failed. Retrying...")
                    time.sleep(10)

# ========================
# MAIN LOOP
# ========================

def main():
    print("🔥 Pocket AI LIVE")

    while True:
        try:
            user_input = input("You: ")

            if user_input.lower() in ["exit", "quit"]:
                break

            reply = smart_ai(user_input)

            print("Bot:", reply)

        except Exception as e:
            print("Main error:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
