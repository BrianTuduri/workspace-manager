#!/usr/bin/env python3

import subprocess
import os
import json
import logging
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

path_profile = os.getenv("PATH_PROFILE")
timeout_between_workspaces = int(os.getenv("TIMEOUT_BETWEEN_WORKSPACES"))
log_level_str = os.getenv("LEVEL_LOGGIN", "INFO")
logging.basicConfig(level=getattr(logging, log_level_str.upper(), logging.INFO))

def check_if_installed(app):
    try:
        subprocess.check_call(["which", app.split()[0]], stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def workspace_exists(workspace_number):
    workspaces_output = subprocess.check_output(["swaymsg", "-t", "get_workspaces"]).decode()
    workspaces = json.loads(workspaces_output)
    return any(workspace['num'] == int(workspace_number) for workspace in workspaces)

def open_in_workspace(workspace_number, command):
    if check_if_installed(command):
        if workspace_exists(workspace_number):
            subprocess.run(["swaymsg", f"workspace number {workspace_number}; exec {command}"])
        else:
            subprocess.run(["swaymsg", f"workspace {workspace_number}; exec {command}"])
        time.sleep(timeout_between_workspaces)
    else:
        logging.error(f'La aplicación "{command}" no está instalada o no se encuentra en el PATH.')

def main():
    profiles_dir = Path(path_profile)

    profiles = [str(f.stem) for f in profiles_dir.glob("*.json")]

    if not profiles:
        logging.error("No se encontraron perfiles.")
        return

    rofi = subprocess.Popen(["rofi", "-dmenu", "-i", "-p", "Select a profile"],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)

    profile, _ = rofi.communicate("\n".join(profiles).encode())
    profile = profile.decode().strip()

    if not profile:
        logging.error("No se seleccionó ningún perfil.")
        return

    try:
        with open(profiles_dir / f'{profile}.json', 'r') as f:
            workspaces = json.load(f)
    except FileNotFoundError:
        logging.error(f"No se encontró el archivo de configuración para el perfil '{profile}'.")
        return

    for workspace, command in workspaces.items():
        open_in_workspace(workspace, command)

if __name__ == "__main__":
    main()
