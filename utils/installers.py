from colorama import Fore, Style
import time

def simulate_installation(package_name, installer="pip"):
    print(Fore.YELLOW + f"[Aegis] Installing '{package_name}' using {installer}...", end="", flush=True)
    time.sleep(1)
    print(Fore.GREEN + " ✅ (simulated)")

def run_installer(package_name, installer="pip"):
    import subprocess

    command = []
    if installer == "pip":
        command = ["pip", "install", package_name]
    elif installer == "npm":
        command = ["npm", "install", "-g", package_name]
    elif installer == "winget":
        command = ["winget", "install", "--id", package_name, "--silent"]
    else:
        print(Fore.RED + f"[Aegis] Unsupported installer: {installer}")
        return

    try:
        print(Fore.YELLOW + f"[Aegis] Running: {' '.join(command)}")
        subprocess.run(command, check=True)
        print(Fore.GREEN + f"[Aegis] Installed '{package_name}' successfully.")
    except subprocess.CalledProcessError:
        print(Fore.RED + f"[Aegis] Failed to install '{package_name}' with {installer}.")
