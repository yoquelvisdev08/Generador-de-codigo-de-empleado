"""
Modelo para templates HTML de carnet
"""
from pathlib import Path
from typing import Optional, Dict, Any, Set
from dataclasses import dataclass, field
import json


@dataclass
class HTMLTemplate:
    """Modelo para representar un template HTML de carnet"""
    
    nombre: str = "Template HTML por Defecto"
    ruta_html: Optional[str] = None
    ancho: int = 637    # 54mm a 300 DPI
    alto: int = 1013   # 85.6mm a 300 DPI (ajustado para coincidir con el HTML)
    dpi: int = 300
    
    def cargar_desde_archivo(self, ruta_html: Path) -> bool:
        """
        Carga un template desde un archivo HTML
        
        Args:
            ruta_html: Ruta al archivo HTML
            
        Returns:
            True si se cargó correctamente
        """
        try:
            if not ruta_html.exists():
                return False
            
            self.ruta_html = str(ruta_html)
            return True
        except Exception as e:
            print(f"Error al cargar template: {e}")
            return False
    
    def detectar_variables(self) -> Set[str]:
        """
        Detecta las variables presentes en el template HTML
        
        Returns:
            Conjunto de nombres de variables encontradas
        """
        if not self.ruta_html:
            return set()
        
        from src.utils.html_parser import obtener_variables_desde_archivo
        return obtener_variables_desde_archivo(Path(self.ruta_html))
    
    def obtener_variables_disponibles(self) -> Dict[str, str]:
        """
        Retorna las variables disponibles en el template
        
        Returns:
            Diccionario con descripciones de variables
        """
        # Detectar variables del template actual
        variables_detectadas = self.detectar_variables()
        
        # Descripciones por defecto
        descripciones = {
            "nombre": "Nombre del empleado",
            "codigo_barras": "Imagen del código de barras (base64)",
            "id_unico": "ID único del empleado",
            "cedula": "Número de cédula",
            "cargo": "Cargo del empleado",
            "empresa": "Nombre de la empresa",
            "web": "Sitio web",
            "foto": "Foto del empleado (base64)"
        }
        
        # Retornar solo las variables encontradas en el template
        resultado = {}
        for var in variables_detectadas:
            resultado[var] = descripciones.get(var, f"Variable: {var}")
        
        return resultado
    
    def generar_variables_ejemplo(self) -> Dict[str, Any]:
        """
        Genera un diccionario con variables de ejemplo
        
        Returns:
            Diccionario con valores de ejemplo
        """
        return {
            "nombre": "Juan Pérez",
            "id_unico": "ABC123XYZ",
            "cedula": "12345678",
            "cargo": "Desarrollador Senior",
            "empresa": "Mi Empresa S.A.",
            "web": "www.miempresa.com",
            "codigo_barras": "",  # Se inyectará como base64
            "foto": ""  # Se inyectará como base64
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el template a un diccionario"""
        return {
            'nombre': self.nombre,
            'ruta_html': self.ruta_html,
            'ancho': self.ancho,
            'alto': self.alto,
            'dpi': self.dpi
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HTMLTemplate':
        """Crea un template desde un diccionario"""
        return cls(**data)
    
    def guardar_metadata(self, ruta_json: Path) -> bool:
        """
        Guarda los metadatos del template en un archivo JSON
        
        Args:
            ruta_json: Ruta donde guardar el JSON
            
        Returns:
            True si se guardó correctamente
        """
        try:
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar metadata: {e}")
            return False
    
    @classmethod
    def cargar_metadata(cls, ruta_json: Path) -> Optional['HTMLTemplate']:
        """
        Carga los metadatos del template desde un archivo JSON
        
        Args:
            ruta_json: Ruta al archivo JSON
            
        Returns:
            HTMLTemplate o None si hay error
        """
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Error al cargar metadata: {e}")
            return None

