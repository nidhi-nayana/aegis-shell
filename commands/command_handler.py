import os
import subprocess
import json
import sys
import importlib
import shutil
from colorama import Fore, Style

# Add the parent directory to sys.path to enable relative imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.installers import install_package, is_python_package_installed
from llm.llm_handler import handle_unknown_command
from config_loader import load_command_mappings, save_command_mappings

def is_command_installed(command):
    """Check if a command exists in the system path."""
    # First check if it's available directly as a command
    try:
        if shutil.which(command) is not None:
            return True
    except Exception:
        pass
    
    # Then try using system-specific commands
    try:
        return subprocess.call(['where' if os.name == 'nt' else 'which', command],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL) == 0
    except Exception:
        return False

def is_package_installed(package_name, language="system"):
    """Check if a package is installed based on language."""
    if language == "python":
        return is_python_package_installed(package_name)
    elif language == "javascript":
        # Check if it's a global npm package
        try:
            result = subprocess.run(['npm', 'list', '-g', package_name], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
            return package_name in result.stdout
        except Exception:
            return False
    else:
        return is_command_installed(package_name)

def handle_command(command, mappings, config):
    """Handle the entered command by checking if it exists and offering installation options."""
    print(f"DEBUG: Checking command: '{command}'")
    print(f"DEBUG: Available mappings: {list(mappings.keys())}")
    
    # Check if it's in our mappings
    is_in_mappings = command in mappings
    if is_in_mappings:
        info = mappings[command]
        print(f"DEBUG: Found mapping for '{command}': {info}")
        language = info.get("language", "system")
        
        # Check if already installed
        if is_package_installed(command, language):
            print(Fore.GREEN + f"[Aegis] '{command}' is already installed ✅")
            return
        
        # Handle multi-language packages
        if language == "multi" and "options" in info:
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
                    install_package(package, installer)
            except (ValueError, IndexError):
                print(Fore.RED + "[Aegis] Invalid selection.")
            return
        
        # Handle normal packages
        if "install_cmd" in info:
            install_cmd = info["install_cmd"]
            installer, package = parse_install_command(install_cmd)
            
            print(Fore.YELLOW + f"[Aegis] '{command}' not found on your system. Installation command: {install_cmd}")
            confirm = input("Do you want to install it? [y/N]: ").strip().lower()
            if confirm == "y":
                install_package(package, installer)
            return
    
    # If command is not in mappings, check if it's installed anyway
    if is_command_installed(command):
        print(Fore.GREEN + f"[Aegis] Command '{command}' exists ✅")
        return
    
    # Unknown command → AI fallback
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
                    success = install_package(pkg, installer)
                    if success:
                        # Update mapping with the new command
                        mappings[command] = {
                            "language": "system" if installer != "pip" else "python",
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
    except Exception as e:
        print(f"Error parsing install command: {e}")
        return None, None