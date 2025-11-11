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

# Asegurar que los directorios existan
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

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

# Configuración de seguridad
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
# Si no hay contraseña configurada, usar una por defecto (se recomienda cambiar)
if not ADMIN_PASSWORD:
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD_DEFAULT", "admin123")

