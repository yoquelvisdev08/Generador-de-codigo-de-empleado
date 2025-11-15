"""
Utilidades para hash y verificación de contraseñas
"""
import hashlib
import secrets
import logging

logger = logging.getLogger(__name__)


def generar_salt() -> str:
    """
    Genera un salt aleatorio para hash de contraseñas
    
    Returns:
        Salt aleatorio en formato hexadecimal
    """
    return secrets.token_hex(16)


def hash_contraseña(contraseña: str, salt: str = None) -> tuple[str, str]:
    """
    Genera el hash de una contraseña usando SHA-256 con salt
    
    Args:
        contraseña: Contraseña en texto plano
        salt: Salt opcional. Si no se proporciona, se genera uno nuevo
        
    Returns:
        Tupla con (hash_hex, salt_hex)
    """
    if salt is None:
        salt = generar_salt()
    
    # Combinar contraseña y salt
    contraseña_salt = contraseña + salt
    
    # Generar hash SHA-256
    hash_obj = hashlib.sha256(contraseña_salt.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    
    return hash_hex, salt


def verificar_contraseña(contraseña: str, hash_almacenado: str, salt: str) -> bool:
    """
    Verifica si una contraseña coincide con el hash almacenado
    
    Args:
        contraseña: Contraseña en texto plano a verificar
        hash_almacenado: Hash almacenado en la base de datos
        salt: Salt usado para generar el hash almacenado
        
    Returns:
        True si la contraseña es correcta, False en caso contrario
    """
    hash_calculado, _ = hash_contraseña(contraseña, salt)
    return hash_calculado == hash_almacenado


def formatear_contraseña_hash(hash_hex: str, salt: str) -> str:
    """
    Formatea el hash y salt en un string único para almacenar en BD
    Formato: hash:salt
    
    Args:
        hash_hex: Hash en hexadecimal
        salt: Salt en hexadecimal
        
    Returns:
        String formateado "hash:salt"
    """
    return f"{hash_hex}:{salt}"


def parsear_contraseña_hash(contraseña_formateada: str) -> tuple[str, str]:
    """
    Parsea un string formateado de contraseña en hash y salt
    
    Args:
        contraseña_formateada: String en formato "hash:salt"
        
    Returns:
        Tupla con (hash_hex, salt_hex)
        
    Raises:
        ValueError: Si el formato no es válido
    """
    partes = contraseña_formateada.split(":")
    if len(partes) != 2:
        raise ValueError(f"Formato de contraseña inválido: {contraseña_formateada}")
    return partes[0], partes[1]

