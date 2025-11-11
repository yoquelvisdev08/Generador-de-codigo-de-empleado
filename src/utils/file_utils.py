"""
Utilidades para manejo de archivos
"""
import os
from typing import List
from pathlib import Path
from config.settings import INVALID_FILENAME_CHARS


def limpiar_nombre_archivo(nombre: str) -> str:
    """
    Limpia un nombre de archivo eliminando caracteres inválidos
    
    Args:
        nombre: Nombre a limpiar
        
    Returns:
        Nombre limpio sin caracteres inválidos
    """
    nombre_limpio = nombre
    for char in INVALID_FILENAME_CHARS:
        nombre_limpio = nombre_limpio.replace(char, '_')
    return nombre_limpio.strip()


def obtener_ruta_imagen(nombre_empleado: str, codigo_barras: str, directorio: Path) -> Path:
    """
    Genera la ruta completa para una imagen de código de barras
    
    Args:
        nombre_empleado: Nombre del empleado
        codigo_barras: Código de barras
        directorio: Directorio base donde se guardarán las imágenes
        
    Returns:
        Path completo al archivo de imagen
    """
    nombre_empleado_limpio = limpiar_nombre_archivo(nombre_empleado or "sin_nombre")
    nombre_archivo = f"{nombre_empleado_limpio}_{codigo_barras}.png"
    return directorio / nombre_archivo


def crear_directorio_si_no_existe(directorio: Path) -> None:
    """
    Crea un directorio si no existe
    
    Args:
        directorio: Path del directorio a crear
    """
    directorio.mkdir(parents=True, exist_ok=True)

