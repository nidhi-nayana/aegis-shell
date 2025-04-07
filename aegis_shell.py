from commands.command_handler import handle_command
from config_loader import load_command_mappings, load_config
from utils.permissions import check_admin_rights
from colorama import Fore, Style, init
import os

init(autoreset=True)

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.CYAN + Style.BRIGHT + "$ aegis-shell")
    print(Fore.YELLOW + "[Aegis] Welcome to the ultimate AI-powered terminal shell.")
    print(Fore.YELLOW + "Type 'exit' to quit.\n")

    mappings = load_command_mappings()
    config = load_config()

    while True:
        cmd = input(Fore.GREEN + Style.BRIGHT + "aegis> " + Style.RESET_ALL).strip()
        if cmd.lower() == "exit":
            print(Fore.CYAN + "[Aegis] Goodbye, warrior! 🛡️")
            break
        if cmd == "":
            continue
        handle_command(cmd, mappings, config)

if __name__ == "__main__":
    if not check_admin_rights():
        print(Fore.RED + "[Aegis] Warning: Admin rights not detected. Some operations may fail.")
    main()
