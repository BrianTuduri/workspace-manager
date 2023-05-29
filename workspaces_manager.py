#!/usr/bin/env python3

import subprocess
import os
import json
import logging
import sys
import time
from pathlib import Path

class AppRunner:
    def __init__(self):
        self.path_file_config = f"{os.path.dirname(os.path.abspath(__file__))}/config.json"
        with open(self.path_file_config, 'r') as f:
            self.config = json.load(f)


        self.path_profile = os.path.expanduser(self.config["PATH_PROFILE"])
        self.menu_program = self.config["MENU_PROGRAM"]
        self.autostart_profile = self.config["AUTOSTART_PROFILE"]
        self.close_all_option = self.config["CLOSE_ALL_OPTION"]
        self.automatic_start = self.config["AUTOMATIC_START"]
        self.timeout_between_workspaces = float(self.config["TIMEOUT_BETWEEN_WORKSPACES"])
        self.log_level_str = self.config["LEVEL_LOGIN"]
        logging.basicConfig(level=getattr(logging, self.log_level_str.upper(), logging.INFO))
        self.log_config()

        if self.automatic_start and self.autostart_profile:
            self.open_profile(self.autostart_profile)

    def log_config(self):
        logging.info(f'path_profile: {self.path_profile}')
        logging.info(f'timeout_between_workspaces: {self.timeout_between_workspaces}')
        logging.info(f'log_level_str: {self.log_level_str}') # Agregando el 'self.'
        logging.info(f'autostart_profile: {self.autostart_profile}')
        logging.info(f'close_all_option: {self.close_all_option}')
        logging.info(f'automatic_start: {self.automatic_start}')

    def show_error_with_menu(self, message):
        with subprocess.Popen([self.menu_program, '--show', 'dmenu'], stdin=subprocess.PIPE) as menu:
            menu.communicate(input=message.encode())

    def check_if_installed(self, app):
        try:
            subprocess.check_call(["which", app.split()[0]], stdout=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            message = f'La aplicación "{app}" no está instalada o no se encuentra en el PATH.'
            logging.error(message)
            self.show_error_with_menu_program(message)
            return False

    def display_menu(self, options):
        with subprocess.Popen([self.menu_program, '--show', 'dmenu'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as menu:
            selected_option, _ = menu.communicate("\n".join(options.keys()).encode())
        selected_option = selected_option.decode().strip()
        if selected_option in options:
            action = options[selected_option]
            if callable(action):
                action()
            elif isinstance(action, dict):
                self.display_menu(action)
            else:
                self.show_error_with_menu_program(f"Opción no reconocida: {selected_option}")

    def open_in_workspace(self, workspace_number, command):
        if self.check_if_installed(command):
            p = subprocess.Popen(["swaymsg", f"exec {command}"])
            time.sleep(self.timeout_between_workspaces)
            subprocess.run(["swaymsg", f"move container to workspace {workspace_number}"])

    def close_all_workspaces(self):
        options = {
            "¿Estás seguro de que quieres cerrar todos los workspaces?" : "",
            "Sí": self._confirm_close_all,
            "No": self.main_menu,
        }
        self.display_menu(options)

    def _confirm_close_all(self):
        try:
            command = "swaymsg -t get_tree | grep '\"pid\"' | awk '{print $2}' | tr -d ',' | xargs kill"
            subprocess.run(command, shell=True, check=True)
            self.main_menu()
        except Exception as e:
            logging.error(f"Error al cerrar los workspaces: {e}")

    def main_menu(self):
        options = {
            'Perfiles': self.main,
        }

        if self.automatic_start:
            options['Arranque automatico'] = self.autostart_menu

        if self.close_all_option:
            options['Cerrar todos los workspaces'] = self.close_all_workspaces

        self.display_menu(options)

    def autostart_menu(self):
        options = {
            'Agregar': self.set_autostart_profile,
            'Borrar': self.clear_autostart_profile if self.autostart_profile else None,
        }

        self.display_menu(options)

    def set_autostart_profile(self):
        profiles_dir = Path(self.path_profile)

        profiles = [str(f.stem) for f in profiles_dir.glob("*.json")]

        if not profiles:
            self.show_error_with_menu_program("No se encontraron perfiles.")
            return

        with subprocess.Popen([self.menu_program, '--show', 'dmenu'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as menu_program:
            profile, _ = menu_program.communicate("\n".join(profiles).encode())
        profile = profile.decode().strip()

        if not profile:
            self.show_error_with_menu_program("No se seleccionó ningún perfil.")
            return

        with open(self.path_file_config, 'r') as f:
            config = json.load(f)
        config['AUTOSTART_PROFILE'] = profile
        with open(self.path_file_config, 'w') as f:
            json.dump(config, f, indent=4)

        self.show_error_with_menu_program(f'Haz seleccionado el perfil {profile} para el arranque automático.')

    def clear_autostart_profile(self):
        with open(self.path_file_config, 'r') as f:
            config = json.load(f)
        config['AUTOSTART_PROFILE'] = ""
        with open(self.path_file_config, 'w') as f:
            json.dump(config, f, indent=4)

        self.show_error_with_menu_program('Has borrado el perfil de arranque automático.')

    def open_profile(self, profile):
        profiles_dir = Path(self.path_profile)

        try:
            with open(profiles_dir / f'{profile}.json', 'r') as f:
                workspaces = json.load(f)
        except FileNotFoundError:
            self.show_error_with_menu_program(f"No se encontró el archivo de configuración para el perfil '{profile}'.")
            return

        for workspace, command in workspaces.items():
            self.open_in_workspace(workspace, command)

    def main(self):
        profiles_dir = Path(self.path_profile)
        profiles = [str(f.stem) for f in profiles_dir.glob("*.json")]

        if not profiles:
            self.show_error_with_menu_program("No se encontraron perfiles.")
            return

        with subprocess.Popen([self.menu_program, '--show', 'dmenu'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as menu_program:
            profile, _ = menu_program.communicate("\n".join(profiles).encode())
        profile = profile.decode().strip()

        if not profile:
            self.show_error_with_menu_program("No se seleccionó ningún perfil.")
            return

        self.open_profile(profile)


if __name__ == "__main__":
    AppRunner().main_menu()
