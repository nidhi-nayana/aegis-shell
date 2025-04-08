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
    """Handle the entered command by checking if it exists and offering installation options."""
    
    # 1. Already installed
    if is_installed(command):
        print(Fore.GREEN + f"[Aegis] Command '{command}' exists ✅")
        return

    # 2. Found in known mappings
    if command in mappings:
        info = mappings[command]
        
        # Handle multi-language packages
        if "language" in info and info["language"] == "multi" and "options" in info:
            options = info["options"]
            print(Fore.YELLOW + f"[Aegis] Found multiple options for '{command}':")
            for i, (env, cmd) in enumerate(options.items(), 1):
                print(f"{i}. {env.capitalize()} (install with {cmd.split()[0]})")
            
            choice = input("Choose option: ").strip()
            try:
                choice_idx = int(choice) - 1
                chosen_env = list(options.keys())[choice_idx]
                install_cmd = options[chosen_env]
                installer, package = parse_install_command(install_cmd)
                if installer and package:
                    simulate_installation(package, installer)
            except (ValueError, IndexError):
                print(Fore.RED + "[Aegis] Invalid selection.")
            return
        
        # Handle normal packages
        if "install_cmd" in info:
            install_cmd = info["install_cmd"]
            installer, package = parse_install_command(install_cmd)
            
            print(Fore.YELLOW + f"[Aegis] '{command}' not found. Suggested: {install_cmd}")
            confirm = input("Do you want to simulate installation? [y/N]: ").strip().lower()
            if confirm == "y":
                simulate_installation(package, installer)
            return

    # 3. Unknown command → AI fallback
    print(Fore.YELLOW + f"[Aegis] Unknown command: '{command}'")
    confirm = input("[Aegis] Would you like me to ask the AI for help? [y/N]: ").strip().lower()
    if confirm != "y":
        return

    suggestion, install_command = handle_unknown_command(command)

    if suggestion:
        print(Fore.MAGENTA + "[LLM AI Response]:")
        print(Fore.WHITE + suggestion)
        
        if install_command:
            confirm2 = input(Fore.YELLOW + "Do you want to install this? [y/N]: ").strip().lower()
            if confirm2 == "y":
                installer, pkg = parse_install_command(install_command)
                if installer and pkg:
                    simulate_installation(pkg, installer)
                    # Update mapping with the new command
                    mappings[command] = {
                        "language": "system",
                        "install_cmd": install_command
                    }
                    save_command_mappings(mappings)
                    print(Fore.GREEN + f"[Aegis] Added '{command}' to known commands.")
                else:
                    print(Fore.RED + "[Aegis] Could not parse install command.")
        else:
            print(Fore.RED + "[Aegis] Could not determine installation method.")
    else:
        print(Fore.RED + "[Aegis] AI could not help with this command.")

def parse_install_command(command_str):
    """Parses installation commands like 'pip install xyz' or 'npm install abc'"""
    try:
        parts = command_str.strip().split()
        if len(parts) >= 3 and parts[1].lower() in ["install", "add"]:
            return parts[0], parts[2]
        elif len(parts) == 2:  # For formats like "apt python3"
            return parts[0], parts[1]
        return None, None
    except Exception:
        return None, None