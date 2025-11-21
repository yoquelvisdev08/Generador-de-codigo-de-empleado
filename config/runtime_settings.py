"""
Configuración en tiempo de ejecución para detectar si la aplicación
está ejecutándose como ejecutable compilado o en modo desarrollo
"""
import sys
import os
from pathlib import Path

def get_base_path():
    """
    Obtiene el directorio base de la aplicación.
    Funciona tanto en desarrollo como en ejecutable compilado.
    """
    if getattr(sys, 'frozen', False):
        # Ejecutable compilado con PyInstaller
        return Path(sys._MEIPASS)
    else:
        # Modo desarrollo
        return Path(__file__).resolve().parent.parent

def get_executable_dir():
    """
    Obtiene el directorio donde está el ejecutable.
    En desarrollo, devuelve el directorio raíz del proyecto.
    """
    if getattr(sys, 'frozen', False):
        # Ejecutable compilado
        return Path(sys.executable).parent
    else:
        # Modo desarrollo
        return Path(__file__).resolve().parent.parent

def get_data_dir():
    """
    Obtiene el directorio de datos de la aplicación.
    En producción usa ProgramData, en desarrollo usa ./data
    """
    if getattr(sys, 'frozen', False):
        # Ejecutable compilado - usar carpeta de datos del sistema
        app_name = "Generador de Códigos de Carnet"
        
        # Intentar leer desde variable de entorno o .env
        from dotenv import load_dotenv
        env_file = get_executable_dir() / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        data_dir_env = os.getenv('DATA_DIR')
        if data_dir_env:
            return Path(data_dir_env)
        
        # Si no hay variable de entorno, usar AppData del usuario (más fácil de acceder)
        if os.name == 'nt':  # Windows
            # Usar AppData\Roaming del usuario en lugar de ProgramData
            base = os.getenv('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
            return Path(base) / app_name
        else:  # Linux/Mac
            return Path.home() / f'.{app_name.lower().replace(" ", "_")}'
    else:
        # Modo desarrollo - usar carpeta local
        return Path(__file__).resolve().parent.parent / "data"

def get_config_dir():
    """
    Obtiene el directorio de configuración.
    """
    base_path = get_base_path()
    return base_path / "config"

def get_assets_dir():
    """
    Obtiene el directorio de assets (logos, iconos).
    """
    base_path = get_base_path()
    return base_path / "assets"

def is_frozen():
    """
    Verifica si la aplicación está ejecutándose como ejecutable compilado.
    """
    return getattr(sys, 'frozen', False)

def get_app_info():
    """
    Retorna información sobre el modo de ejecución de la aplicación.
    """
    return {
        'frozen': is_frozen(),
        'base_path': str(get_base_path()),
        'executable_dir': str(get_executable_dir()),
        'data_dir': str(get_data_dir()),
        'config_dir': str(get_config_dir()),
        'assets_dir': str(get_assets_dir()),
        'python_version': sys.version,
        'platform': sys.platform,
    }

