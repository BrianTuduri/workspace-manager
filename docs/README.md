### Workspace Manager

## Resumen
Workspace Manager es un script de Python diseñado para crear y cambiar entre diferentes "perfiles" de trabajo. Cada perfil de trabajo define qué aplicaciones se deben abrir en qué workspaces, y los perfiles pueden ser seleccionados fácilmente a través de rofi o wofi.

## Instalación

Para usar Workspace Manager, primero deberá crear uno o más perfiles de trabajo. Luego, puede seleccionar un perfil a través de `rofi` o `wofi` y el script abrirá automáticamente las aplicaciones especificadas en los workspaces correspondientes.

Solamente se debe clonar el repositorio, verificar la [configuración](#Configuración) y [ajustar su atajo de preferencia](#configuración-de-los-atajos-de-teclado).

```bash
git clone https://github.com/BrianTuduri/workspace-manager.git ~/workspace_manager
```

## Configuración

En el directorio raiz existe un archivo `config.json` en este se pueden ajustar ciertas configuraciones, estas son:

```json
{
  "PATH_PROFILE": "~/workspace_manager/profiles", // Directorio de perfiles

  "MENU_PROGRAM": "wofi", // Se puede utilizar este script con rofi o wofi, estos son los valores que deben ir aqui.

  "TIMEOUT_BETWEEN_WORKSPACES": 0.6, // Timeout para abrir workspaces con aplicaciones

  "CLOSE_ALL_OPTION": true, // Habilitar opción para cerrar todos los workspaces

  "AUTOMATIC_START": true, // Habilitar opción para setear perfiles con arranque automático

  "AUTOSTART_PROFILE": "", // Este valor lo configura solo el script, en caso de querer configurarlo manualmente, aqui debe ir el nonmbre de tu perfil.

  "LEVEL_LOGIN": "INFO" // Nivel de log
}

```
## Creación de perfiles

Los perfiles de trabajo se definen en archivos JSON en el directorio que se especifique. Cada archivo JSON debe contener un objeto de mapeo de números de workspaces a comandos de aplicaciones.

Por ejemplo, un archivo JSON de perfil podría verse así:


```json
{
    "1": "firefox",
    "2": "codium",
    "3": "kitty"
}
```
En este ejemplo, seleccionar este perfil abrirá Firefox en el workspace 1, Codium en el workspace 2, y Kitty en el workspace 3 (el perfil tendra como titulo el nombre de tu archivo json).

## Selección de perfiles

Los perfiles se pueden seleccionar a través del menú que se configuro. Puede lanzar rofi o wofi y seleccionar un perfil usando el atajo de teclado definido en su archivo de configuración de su entorno.

## Configuración de los atajos de teclado

Para configurar un atajo de teclado para lanzar el Workspace Manager, agregue una línea como la siguiente a su archivo de configuración de su entorno:

```bash
bindsym $mod+Shift+i exec /home/user/workspace_manager/workspaces_manager.py
```

En este ejemplo, la combinación de teclas mod+Shift+i lanzará el Workspace Manager.

## Funcionamiento

Existen 3 menús actualmente:

↪ [`Perfiles`](#perfiles)

↪ [`Arranque automático`](#arranque-automático)

↪ [`Cerrar todos los workspaces`](#cerrar-todos-los-workspaces)

### `Perfiles`
Cuando selecciona un perfil, Workspace Manager lee la configuración del perfil de un archivo JSON, verifica si las aplicaciones especificadas están instaladas y si los workspaces especificados existen. Si la aplicación está instalada, la abre en el workspace correspondiente. Si el workspace no existe, lo crea y luego abre la aplicación.

### `Arranque automático`
Similar a lo que realice perfiles, siendo que este modo tiene dos submenús, `(agregar/borrar)`. Si agregas perfiles para el arranque automático estos se ejecutarán junto al inicio de tu sistema.

Si quieres habilitar esta opción debes agregar una línea a tu archivo de configuración de tu gestor de escritorio (generalmente ubicado en ~/.config/*/config), hazlo de la siguiente de la siguiente manera:

Usaremos a `sway` de ejemplo

```bash
sudo nano ~/.config/sway/config 
```

Y debes agregar esta línea

```bash
exec_always python3 $HOME/workspace_manager/workspaces_manager.py
```

Reemplaza "$HOME/workspace_manager/workspaces_manager.py" con la ruta completa a tu script de Python. exec_always ejecutará el comando cada vez que se recargue el archivo de configuración de sway, lo que significa que se ejecutará al inicio y cada vez que ejecutes cambios en la configuración de tu entorno.

### `Cerrar todos los workspaces`
Este es un menú simple el cual te solicitara una confirmación `[Si/No]` para comprobar que estás seguro de que quieres cerrar todos los workspaces.


## Advertencia

Tenga en cuenta que Workspace Manager asume que todas las aplicaciones especificadas en los perfiles de trabajo están instaladas y disponibles en su PATH. Si una aplicación no está instalada o no está en su PATH, el script registrará un error, pero seguirá procesando el resto del perfil.
