### Workspace Manager

## Resumen
Workspace Manager es un script de Python diseñado para crear y cambiar entre diferentes "perfiles" de trabajo. Cada perfil de trabajo define qué aplicaciones se deben abrir en qué workspaces, y los perfiles pueden ser seleccionados fácilmente a través de rofi.

## Uso

Para usar Workspace Manager, primero deberá crear uno o más perfiles de trabajo. Luego, puede seleccionar un perfil a través de rofi y el script abrirá automáticamente las aplicaciones especificadas en los workspaces correspondientes.

Por favor `instalar el modulo dotenv` con pip.

```
pip3 install python-dotenv
```

## Configuración

En el directorio raiz existe un archivo `.env` en este se pueden ajustar ciertas configuraciones, estas son:
```
PATH_PROFILE=/home/user/workspace-manager/profiles => Directorio de perfiles

TIMEOUT_BETWEEN_WORKSPACES=1 => Timeout para abrir workspaces con aplicaciones

LEVEL_LOGGIN=INFO => Nivel de log

```
## Creación de perfiles

Los perfiles de trabajo se definen en archivos JSON en el directorio que se especifique. Cada archivo JSON debe contener un objeto de mapeo de números de workspaces a comandos de aplicaciones.

Por ejemplo, un archivo JSON de perfil podría verse así:


```
{
    "1": "firefox",
    "2": "codium",
    "3": "kitty"
}
```
En este ejemplo, seleccionar este perfil abrirá Firefox en el workspace 1, Codium en el workspace 2, y Kitty en el workspace 3 (el perfil tendra como titulo el nombre de tu archivo json).

## Selección de perfiles

Los perfiles se pueden seleccionar a través de rofi. Puede lanzar rofi y seleccionar un perfil utilizando el atajo de teclado definido en su archivo de configuración de Sway WM.

## Configuración de los atajos de teclado

Para configurar un atajo de teclado para lanzar el Workspace Manager, agregue una línea como la siguiente a su archivo de configuración de Sway WM:

```
bindsym $mod+Shift+i exec /home/user/workspace-manager/workspaces_manager.py
```

En este ejemplo, la combinación de teclas mod+Shift+i lanzará el Workspace Manager.

## Funcionamiento

Cuando selecciona un perfil, Workspace Manager lee la configuración del perfil de un archivo JSON, verifica si las aplicaciones especificadas están instaladas y si los workspaces especificados existen. Si la aplicación está instalada, la abre en el workspace correspondiente. Si el workspace no existe, lo crea y luego abre la aplicación.

## Advertencia

Tenga en cuenta que Workspace Manager asume que todas las aplicaciones especificadas en los perfiles de trabajo están instaladas y disponibles en su PATH. Si una aplicación no está instalada o no está en su PATH, el script registrará un error pero seguirá procesando el resto del perfil.
