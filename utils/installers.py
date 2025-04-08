from colorama import Fore, Style
import subprocess
import importlib
import sys
import time
import os
import re

# Import the new animator
from utils.download_animation import DownloadAnimator

def is_python_package_installed(package_name):
    """Check if a Python package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def get_package_size(package_name, installer="pip"):
    """Get approximate package size in KB (for more realistic progress)"""
    # This is a simplified approach - in a real app, you might want to query
    # package repositories for actual size information
    try:
        if installer == "pip":
            # Get package info but don't show output
            process = subprocess.run(
                ["pip", "search", package_name], 
                capture_output=True, 
                text=True
            )
            # Just return a random reasonable size for demonstration
            return 2048  # 2MB default size
        elif installer == "npm":
            return 5120  # 5MB default size
        elif installer == "winget":
            return 15360  # 15MB default size (apps are larger)
        else:
            return 1024  # 1MB default
    except:
        return 1024  # Default fallback size

def extract_progress_info(line):
    """Extract progress percentage from installer output lines"""
    # For winget style progress
    winget_match = re.search(r'(\d+)%', line)
    if winget_match:
        return int(winget_match.group(1))
    
    # For pip style progress (more complex, simplified here)
    pip_match = re.search(r'Downloading.*\((\d+)/(\d+)\)', line)
    if pip_match:
        current, total = map(int, pip_match.groups())
        return int(current / total * 100)
        
    return None

def install_package(package_name, installer="pip"):
    """Actually install a package using the specified installer with progress animation."""
    print(Fore.YELLOW + f"[Aegis] Preparing to install '{package_name}' using {installer}...")
    
    command = []
    if installer == "pip":
        command = ["pip", "install", package_name, "--progress-bar", "on"]
    elif installer == "npm":
        command = ["npm", "install", "-g", package_name]
    elif installer == "winget":
        command = ["winget", "install", package_name]
    else:
        print(Fore.RED + f"[Aegis] Unsupported installer: {installer}")
        return False

    # Create and start the download animator
    animator = DownloadAnimator(package_name, installer)
    animator.start()

    try:
        # Start the process with pipe for stdout to capture output
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True,
            bufsize=1
        )
        
        # Read output line by line to update progress
        for line in iter(process.stdout.readline, ''):
            # Update the animation based on output (when possible)
            progress = extract_progress_info(line)
            if progress is not None:
                animator.progress = progress
                
            # If we detect certain keywords, boost progress
            if "Installing" in line or "Downloaded" in line:
                animator.update_progress(10)
            elif "Extracting" in line:
                animator.update_progress(5)
            
        # Wait for process to complete
        return_code = process.wait()
        
        # Stop the animation
        animator.stop(return_code == 0)
        
        return return_code == 0
        
    except Exception as e:
        animator.stop(False)
        print(Fore.RED + f"[Aegis] Error installing '{package_name}': {str(e)}")
        return False