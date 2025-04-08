from colorama import Fore, Style
import subprocess
import importlib
import sys

def is_python_package_installed(package_name):
    """Check if a Python package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name, installer="pip"):
    """Actually install a package using the specified installer."""
    print(Fore.YELLOW + f"[Aegis] Installing '{package_name}' using {installer}...")
    
    command = []
    if installer == "pip":
        command = ["pip", "install", package_name]
    elif installer == "npm":
        command = ["npm", "install", "-g", package_name]
    elif installer == "winget":
        command = ["winget", "install", package_name]
    else:
        print(Fore.RED + f"[Aegis] Unsupported installer: {installer}")
        return False

    try:
        print(Fore.YELLOW + f"[Aegis] Running: {' '.join(command)}")
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        print(Fore.GREEN + f"[Aegis] Installed '{package_name}' successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"[Aegis] Failed to install '{package_name}' with {installer}.")
        if hasattr(e, 'stderr') and e.stderr:
            print(Fore.RED + f"Error: {e.stderr}")
        return False