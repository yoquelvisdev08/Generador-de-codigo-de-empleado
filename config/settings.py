"""
Configuración de la aplicación
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE)

DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "codigos_generados"
DB_PATH = DATA_DIR / "codigos_barras.db"
BACKUPS_DIR = DATA_DIR / "backups"
CARNETS_DIR = DATA_DIR / "carnets"
TEMPLATES_DIR = DATA_DIR / "templates_carnet"

# Asegurar que los directorios existan
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
CARNETS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Configuración de la aplicación
APP_NAME = "Generador de Códigos de Barras"
APP_AUTHOR = "by yoquelvisdev"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Configuración de códigos de barras
BARCODE_FORMATS = {
    "Code128": {"max_length": 80, "description": "Acepta caracteres alfanuméricos"},
    "EAN13": {"max_length": 13, "description": "Requiere exactamente 13 dígitos numéricos"},
    "EAN8": {"max_length": 8, "description": "Requiere exactamente 8 dígitos numéricos"},
    "Code39": {"max_length": 43, "description": "Acepta caracteres alfanuméricos y algunos especiales"}
}

# Configuración de generación de imágenes
BARCODE_IMAGE_OPTIONS = {
    'format': 'PNG',
    'module_width': 0.5,
    'module_height': 15,
    'quiet_zone': 6.5,
    'font_size': 10,
    'text_distance': 5.0,
    'background': 'white',
    'foreground': 'black',
    'write_text': True
}

# Caracteres inválidos para nombres de archivo
INVALID_FILENAME_CHARS = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']

# Configuración de seguridad y usuarios
def cargar_usuarios():
    """
    Carga los usuarios desde las variables de entorno ADMIN_USERS y REGULAR_USERS
    Formato ADMIN_USERS: usuario:contraseña,usuario2:contraseña2
    Formato REGULAR_USERS: usuario:contraseña,usuario2:contraseña2
    
    Returns:
        dict: Diccionario con {usuario: {'password': str, 'rol': str}}
    """
    usuarios = {}
    
    # Cargar administradores
    admin_users_str = os.getenv("ADMIN_USERS", "")
    if admin_users_str:
        for usuario_info in admin_users_str.split(","):
            usuario_info = usuario_info.strip()
            if not usuario_info:
                continue
            
            partes = usuario_info.split(":")
            if len(partes) == 2:
                usuario, password = partes
                usuarios[usuario.strip()] = {
                    "password": password.strip(),
                    "rol": "admin"
                }
    
    # Cargar usuarios regulares
    regular_users_str = os.getenv("REGULAR_USERS", "")
    if regular_users_str:
        for usuario_info in regular_users_str.split(","):
            usuario_info = usuario_info.strip()
            if not usuario_info:
                continue
            
            partes = usuario_info.split(":")
            if len(partes) == 2:
                usuario, password = partes
                usuarios[usuario.strip()] = {
                    "password": password.strip(),
                    "rol": "user"
                }
    
    # Si no se cargaron usuarios, crear un usuario admin por defecto
    if not usuarios:
        usuarios = {
            "admin": {
                "password": os.getenv("ADMIN_PASSWORD", "admin123"),
                "rol": "admin"
            }
        }
    
    return usuarios

USUARIOS = cargar_usuarios()

def autenticar_usuario(usuario: str, password: str) -> tuple[bool, str]:
    """
    Autentica un usuario y retorna su rol si es válido
    
    Args:
        usuario: Nombre de usuario
        password: Contraseña
        
    Returns:
        tuple: (es_valido: bool, rol: str)
        Si es_valido es False, rol será una cadena vacía
    """
    if usuario in USUARIOS:
        if USUARIOS[usuario]["password"] == password:
            return True, USUARIOS[usuario]["rol"]
    return False, ""

# Mantener compatibilidad con código antiguo
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

