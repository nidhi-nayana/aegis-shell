import os
import sys
# Ensure current directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from commands.command_handler import handle_command
from config_loader import load_command_mappings, load_config
from utils.permissions import check_admin_rights
from colorama import Fore, Style, init
init(convert=True)
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

init(autoreset=True)

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.CYAN + Style.BRIGHT + "$ aegis-shell")
    print(Fore.YELLOW + "[Aegis] Welcome to the ultimate AI-powered terminal shell.")
    print(Fore.YELLOW + "Type 'exit' to quit.\n")

    try:
        mappings = load_command_mappings()
        print(f"DEBUG: Loaded {len(mappings)} command mappings")
    except Exception as e:
        print(f"Error loading mappings: {e}")
        mappings = {}
    
    config = load_config()
    
    # Setup advanced autocomplete using prompt_toolkit
    command_completer = WordCompleter(list(mappings.keys()), ignore_case=True)
    session = PromptSession(message="aegis> ", completer=command_completer)

    while True:
        try:
            cmd = session.prompt().strip()
            if cmd.lower() == "exit":
                print(Fore.CYAN + "[Aegis] Goodbye, warrior! 🛡️")
                break
            if cmd == "":
                continue
            handle_command(cmd, mappings, config)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            print(Fore.RED + f"[Aegis] Error: {e}")

if __name__ == "__main__":
    if not check_admin_rights():
        print(Fore.RED + "[Aegis] Warning: Admin rights not detected. Some operations may fail.")
    main()