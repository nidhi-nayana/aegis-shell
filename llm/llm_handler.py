import requests
from colorama import Fore, Style
import re

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

MODEL = "google/gemini-2.0-flash-thinking-exp-1219:free"

def handle_unknown_command(command: str):
    """
    Ask the LLM about an unknown command and return both the explanation
    and an extracted installation command if available.
    """
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
                    "The installation command should be in the format: 'package-manager install package-name'\n"
                    "Common package managers include pip, npm, gem, apt, brew, etc.\n"
                    "DO NOT add anything else, just respond with a clean single paragraph."
                )
            },
            {
                "role": "user",
                "content": f"The user typed: '{command}'"
            }
        ]
    }
    
    try:
        print(Fore.BLUE + f"[Aegis Debug] Sending request to API with model: {MODEL}" + Style.RESET_ALL)
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"].strip()
            
            # Extract installation command from the response
            install_cmd = None
            if "run:" in reply.lower():
                install_parts = reply.split("run:")
                if len(install_parts) > 1:
                    # Extract the first line after "run:"
                    install_cmd = install_parts[1].strip().split("\n")[0].strip()
            
            return reply, install_cmd
        else:
            print(Fore.RED + f"[Aegis] LLM failed: {response.status_code} {response.reason}" + Style.RESET_ALL)
            print(Fore.RED + f"Response: {response.text}" + Style.RESET_ALL)
            return None, None
    except Exception as e:
        print(Fore.RED + f"[Aegis] LLM Error: {e}" + Style.RESET_ALL)
        return None, None