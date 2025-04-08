import json
import os

COMMAND_MAPPINGS_FILE = "config/command_mapping.json"
CONFIG_FILE = "config/config.json"

def load_command_mappings():
    if not os.path.exists(COMMAND_MAPPINGS_FILE):
        return {}
    with open(COMMAND_MAPPINGS_FILE, "r") as f:
        return json.load(f)

def save_command_mappings(mappings):
    with open(COMMAND_MAPPINGS_FILE, "w") as f:
        json.dump(mappings, f, indent=4)

def update_command_mapping(command, environment, package_name, install_method):
    mappings = load_command_mappings()

    if command not in mappings:
        mappings[command] = {}

    mappings[command][environment] = {
        "package": package_name,
        "install": install_method
    }

    save_command_mappings(mappings)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)
