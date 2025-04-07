import requests
from colorama import Fore, Style

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

MODEL = "google/gemini-2.0-flash-thinking-exp:free"

def handle_unknown_command(command: str) -> str | None:
    print(Fore.YELLOW + f"[Aegis AI] Thinking about: '{command}'..." + Style.RESET_ALL)

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an AI inside a developer CLI shell. "
                    "A user typed an unknown command. Your task is to analyze what it might be. "
                    "Respond very briefly in this format:\n\n"
                    "Based on analysis, '<command>' might be a CLI tool used for XYZ. "
                    "To install it, run: <installation command>\n\n"
                    "DO NOT add anything else, just respond with a clean single paragraph like that."
                )
            },
            {
                "role": "user",
                "content": f"The user typed: '{command}'"
            }
        ]
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            return Fore.CYAN + "[LLM AI Response]:\n" + Fore.GREEN + reply.strip() + Style.RESET_ALL
        else:
            print(Fore.RED + f"[Aegis] LLM failed: {response.status_code} {response.reason}" + Style.RESET_ALL)
            return None
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[Aegis] LLM Error: {e}" + Style.RESET_ALL)
        return None