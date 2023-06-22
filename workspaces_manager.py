#!/usr/bin/env python3

import subprocess
import os
import json
import logging
import sys
import time
import argparse
from pathlib import Path

class AppRunner:
    def __init__(self,autostart):
        self.load_config()
        self.log_config()

        # autostart
        if autostart and self.autostart_profile:
            self.open_profile(self.autostart_profile)

    def load_config(self):
        """Carga la configuración desde el archivo config.json"""
        self.path_file_config = Path(__file__).resolve().parent / "config.json"
        try:
            with self.path_file_config.open('r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            logging.error("No se pudo encontrar el archivo config.json.")
            sys.exit(1)

        self.path_profile = Path(os.path.expanduser(self.config["PATH_PROFILE"]))
        self.menu_program = self.config["MENU_PROGRAM"]
        self.autostart_profile = self.config["AUTOSTART_PROFILE"]
        self.close_all_option = self.config["CLOSE_ALL_OPTION"]
        self.automatic_start = self.config["AUTOMATIC_START"]
        self.timeout_between_workspaces = float(self.config["TIMEOUT_BETWEEN_WORKSPACES"])
        self.log_level_str = self.config["LEVEL_LOGIN"]
        logging.basicConfig(level=getattr(logging, self.log_level_str.upper(), logging.INFO))

    def log_config(self):
        """Registra la configuración actual"""
        logging.info(f'path_profile: {self.path_profile}')
        logging.info(f'timeout_between_workspaces: {self.timeout_between_workspaces}')
        logging.info(f'log_level_str: {self.log_level_str}')
        logging.info(f'autostart_profile: {self.autostart_profile}')
        logging.info(f'close_all_option: {self.close_all_option}')
        logging.info(f'automatic_start: {self.automatic_start}')

    def show_error_with_menu(self, message):
        """Muestra un mensaje de error utilizando el programa de menú"""
        with subprocess.Popen([self.menu_program, '--show', 'dmenu'], stdin=subprocess.PIPE) as menu:
            menu.communicate(input=message.encode())

    def check_if_installed(self, app):
        """Verifica si una aplicación está instalada"""
        try:
            subprocess.check_call(["which", app.split()[0]], stdout=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            message = f'La aplicación "{app}" no está instalada o no se encuentra en el PATH.'
            logging.error(message)
            self.show_error_with_menu(message)
            return False

    def display_menu(self, options):
        """Muestra un menú con las opciones proporcionadas"""
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
                self.show_error_with_menu(f"Opción no reconocida: {selected_option}")

    def open_in_workspace(self, workspace_number, command):
        """Abre una aplicación en un espacio de trabajo específico"""
        if self.check_if_installed(command):
            p = subprocess.Popen(["swaymsg", f"exec {os.path.expanduser(command)}"])
            time.sleep(self.timeout_between_workspaces)
            subprocess.run(["swaymsg", f"move container to workspace number {workspace_number}"], check=True)

    def close_all_workspaces(self):
        """Cierra todos los espacios de trabajo después de una confirmación"""
        options = {
            "¿Estás seguro de que quieres cerrar todos los workspaces?" : "",
            "Sí": self._confirm_close_all,
            "No": self.main_menu,
        }
        self.display_menu(options)

    def _confirm_close_all(self):
        """Confirma y cierra todos los espacios de trabajo"""
        try:
            command = "swaymsg -t get_tree | grep '\"pid\"' | awk '{print $2}' | tr -d ',' | xargs kill"
            subprocess.run(command, shell=True, check=True)
            self.main_menu()
        except Exception as e:
            logging.error(f"Error al cerrar los workspaces: {e}")

    def main_menu(self):
        """Muestra el menú principal"""
        options = {
            'Perfiles': self.main,
        }

        if self.automatic_start:
            options['Arranque automatico'] = self.autostart_menu

        if self.close_all_option:
            options['Cerrar todos los workspaces'] = self.close_all_workspaces

        self.display_menu(options)

    def autostart_menu(self):
        """Muestra el menú de inicio automático"""
        options = {
            'Agregar': self.set_autostart_profile,
            'Borrar': self.clear_autostart_profile if self.autostart_profile else None,
        }

        if not options['Borrar']:
            del options['Borrar']

        self.display_menu(options)

    def set_autostart_profile(self):
        """Establece el perfil de inicio automático"""
        profiles = [str(f.stem) for f in self.path_profile.glob("*.json")]

        if not profiles:
            self.show_error_with_menu("No se encontraron perfiles.")
            return

        with subprocess.Popen([self.menu_program, '--show', 'dmenu'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as menu_program:
            profile, _ = menu_program.communicate("\n".join(profiles).encode())
        profile = profile.decode().strip()

        if not profile:
            self.show_error_with_menu("No se seleccionó ningún perfil.")
            return

        with self.path_file_config.open('r') as f:
            config = json.load(f)
        config['AUTOSTART_PROFILE'] = profile
        with self.path_file_config.open('w') as f:
            json.dump(config, f, indent=4)

        self.show_error_with_menu(f'Haz seleccionado el perfil {profile} para el arranque automático.')

    def clear_autostart_profile(self):
        """Borra el perfil de inicio automático"""
        with self.path_file_config.open('r') as f:
            config = json.load(f)
        config['AUTOSTART_PROFILE'] = ""
        with self.path_file_config.open('w') as f:
            json.dump(config, f, indent=4)

        self.show_error_with_menu('Has borrado el perfil de arranque automático.')

    def open_profile(self, profile):
        """Abre un perfil específico"""
        try:
            with (self.path_profile / f'{profile}.json').open('r') as f:
                workspaces = json.load(f)
        except FileNotFoundError:
            self.show_error_with_menu(f"No se encontró el archivo de configuración para el perfil '{profile}'.")
            return

        for workspace, command in workspaces.items():
            self.open_in_workspace(workspace, command)

    def main(self):
        """Muestra el menú principal"""
        profiles = [str(f.stem) for f in self.path_profile.glob("*.json")]

        if not profiles:
            self.show_error_with_menu("No se encontraron perfiles.")
            return

        with subprocess.Popen([self.menu_program, '--show', 'dmenu'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as menu_program:
            profile, _ = menu_program.communicate("\n".join(profiles).encode())
        profile = profile.decode().strip()

        if not profile:
            self.show_error_with_menu("No se seleccionó ningún perfil.")
            return

        self.open_profile(profile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--autostart", action="store_true", help="Ejecuta el arranque automático")
    args = parser.parse_args()
    AppRunner(args.autostart).main_menu()
