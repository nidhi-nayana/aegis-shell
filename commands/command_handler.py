import os
import subprocess
import json
from colorama import Fore, Style
from utils.installers import simulate_installation, run_installer
from llm.llm_handler import handle_unknown_command
from config_loader import load_command_mappings, save_command_mappings
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def is_installed(command):
    """Check if a command exists in the system path."""
    return subprocess.call(['where' if os.name == 'nt' else 'which', command],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL) == 0

def handle_command(command, mappings, config):
    print(Fore.CYAN + f"\naegis> {command}")
    
    # 1. Already installed
    if is_installed(command):
        print(Fore.GREEN + f"[Aegis] Command '{command}' exists ✅")
        return

    # 2. Found in known mappings
    if command in mappings:
        info = mappings[command]
        
        # Multiple environments
        if isinstance(info, dict) and "python" in info and "javascript" in info:
            print(Fore.YELLOW + f"[Aegis] Found multiple options for '{command}':")
            print("1. Python (install with pip)")
            print("2. JavaScript (install with npm)")
            choice = input("Choose [1/2]: ").strip()
            if choice == "1":
                package = info["python"]
                simulate_installation(package, "pip")
            elif choice == "2":
                package = info["javascript"]
                simulate_installation(package, "npm")
            else:
                print(Fore.RED + "[Aegis] Invalid selection.")
        else:
            # Single environment
            if isinstance(info, str):
                installer = "pip" if info.startswith("pip") else "npm" if info.startswith("npm") else "winget"
                package_name = info.split()[-1]
            else:
                installer = info.get("installer", "pip")
                package_name = info.get("package", command)

            print(Fore.YELLOW + f"[Aegis] '{command}' not found. Suggested: install via '{installer} install {package_name}'")
            confirm = input("Do you want to simulate installation? [y/N]: ").strip().lower()
            if confirm == "y":
                simulate_installation(package_name, installer)
        return

    # 3. Unknown command → AI fallback
    print(Fore.YELLOW + f"[Aegis] Unknown command: '{command}'")
    confirm = input("[Aegis] Would you like me to ask the AI for help? [y/N]: ").strip().lower()
    if confirm != "y":
        return

    print(Fore.BLUE + f"[Aegis AI] Thinking about: '{command}'...")
    suggestion, install_command = handle_unknown_command(command)

    if suggestion:
        print(Fore.MAGENTA + "[LLM AI Response]:")
        print(Fore.WHITE + suggestion)
        confirm2 = input(Fore.YELLOW + "Do you want to install this? [y/N]: ").strip().lower()
        if confirm2 == "y" and install_command:
            installer, pkg = parse_install_command(install_command)
            if installer and pkg:
                simulate_installation(pkg, installer)
                # Update mapping
                mappings[command] = f"{installer} install {pkg}"
                save_command_mappings(mappings)
            else:
                print(Fore.RED + "[Aegis] Could not parse install command.")
    else:
        print(Fore.RED + "[Aegis] AI could not help with this command.")

def parse_install_command(command_str):
    """Parses a string like 'pip install xyz' into ('pip', 'xyz')"""
    try:
        parts = command_str.strip().split()
        if len(parts) >= 3:
            return parts[0], parts[2]
        elif len(parts) == 2:
            return parts[0], parts[1]
        return None, None
    except Exception:
        return None, None
