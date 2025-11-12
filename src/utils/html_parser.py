"""
Utilidades para parsear y analizar templates HTML
"""
import re
from typing import List, Set
from pathlib import Path


def detectar_variables_en_html(html_content: str) -> Set[str]:
    """
    Detecta todas las variables {{variable}} en un template HTML
    
    Args:
        html_content: Contenido HTML a analizar
        
    Returns:
        Conjunto de nombres de variables encontradas (sin las llaves)
    """
    # Patrón para encontrar {{variable}}
    patron = r'\{\{([^}]+)\}\}'
    matches = re.findall(patron, html_content)
    
    # Limpiar espacios y obtener variables únicas
    variables = set()
    for match in matches:
        var = match.strip()
        if var:
            variables.add(var)
    
    return variables


def obtener_variables_desde_archivo(ruta_html: Path) -> Set[str]:
    """
    Obtiene las variables desde un archivo HTML
    
    Args:
        ruta_html: Ruta al archivo HTML
        
    Returns:
        Conjunto de nombres de variables
    """
    try:
        if not ruta_html.exists():
            return set()
        
        contenido = ruta_html.read_text(encoding='utf-8')
        return detectar_variables_en_html(contenido)
    except Exception as e:
        print(f"Error al leer archivo HTML: {e}")
        return set()

