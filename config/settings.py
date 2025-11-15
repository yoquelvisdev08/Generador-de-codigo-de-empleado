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
LOGS_DIR = DATA_DIR / "logs"

# Asegurar que los directorios existan
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
CARNETS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Configuración de la aplicación
APP_NAME = "Generador de Códigos de Carnet"
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
# NOTA: La autenticación ahora se realiza mediante base de datos
# Este código se mantiene solo para compatibilidad con código antiguo

def autenticar_usuario(usuario: str, password: str) -> tuple[bool, str]:
    """
    Autentica un usuario usando la base de datos y retorna su rol si es válido
    
    Args:
        usuario: Nombre de usuario
        password: Contraseña en texto plano
        
    Returns:
        tuple: (es_valido: bool, rol: str)
        Si es_valido es False, rol será una cadena vacía
    """
    from src.models.database import DatabaseManager
    from src.utils.password_utils import hash_contraseña, formatear_contraseña_hash, parsear_contraseña_hash
    
    try:
        db_manager = DatabaseManager()
        
        # Obtener usuario de la BD
        usuario_data = db_manager.obtener_usuario_por_usuario(usuario)
        if not usuario_data:
            return False, ""
        
        # Obtener el hash almacenado (formato: hash:salt)
        # Necesitamos obtener la contraseña completa de la BD
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT contraseña FROM usuarios WHERE usuario = ?", (usuario,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, ""
            
            contraseña_formateada = resultado[0]
            hash_almacenado, salt = parsear_contraseña_hash(contraseña_formateada)
        
        # Verificar contraseña
        hash_calculado, _ = hash_contraseña(password, salt)
        
        if hash_calculado == hash_almacenado:
            return True, usuario_data['rol']
        
        return False, ""
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al autenticar usuario: {e}")
        return False, ""

# Mantener compatibilidad con código antiguo (ya no se usa)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

