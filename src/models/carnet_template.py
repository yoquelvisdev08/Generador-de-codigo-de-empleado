"""
Modelo para plantillas de diseño de carnet
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class CarnetTemplate:
    """Modelo para representar una plantilla de diseño de carnet"""
    
    nombre: str = "Plantilla por Defecto"
    
    # Dimensiones del carnet (en píxeles a 300 DPI)
    # Tamaño real de la tarjeta: 54mm x 85.6mm
    ancho: int = 637    # 54mm a 300 DPI (54 * 300 / 25.4)
    alto: int = 1010   # 85.6mm a 300 DPI (85.6 * 300 / 25.4)
    
    # Logo
    logo_path: Optional[str] = None
    logo_x: int = 50
    logo_y: int = 50
    logo_ancho: int = 150
    logo_alto: int = 150
    
    # Fondo
    fondo_color: str = "#FFFFFF"  # Blanco por defecto
    fondo_imagen_path: Optional[str] = None
    fondo_opacidad: float = 1.0
    
    # Campos de texto
    mostrar_nombre: bool = True
    nombre_x: int = 250
    nombre_y: int = 200
    nombre_fuente: str = "Arial"
    nombre_tamaño: int = 24
    nombre_color: str = "#000000"
    nombre_negrita: bool = True
    
    mostrar_cedula: bool = True
    cedula_x: int = 250
    cedula_y: int = 250
    cedula_fuente: str = "Arial"
    cedula_tamaño: int = 18
    cedula_color: str = "#000000"
    cedula_negrita: bool = False
    
    mostrar_cargo: bool = False
    cargo_x: int = 250
    cargo_y: int = 300
    cargo_fuente: str = "Arial"
    cargo_tamaño: int = 16
    cargo_color: str = "#666666"
    cargo_negrita: bool = False
    
    # Código de barras
    codigo_barras_x: int = 250
    codigo_barras_y: int = 450
    codigo_barras_ancho: int = 400
    codigo_barras_alto: int = 100
    mostrar_numero_codigo: bool = True
    numero_codigo_fuente: str = "Arial"
    numero_codigo_tamaño: int = 14
    numero_codigo_color: str = "#000000"
    
    # Foto del empleado
    mostrar_foto: bool = True
    foto_x: int = 50
    foto_y: int = 200
    foto_ancho: int = 150
    foto_alto: int = 200
    
    # Información adicional
    mostrar_empresa: bool = False
    empresa_texto: str = ""
    empresa_x: int = 50
    empresa_y: int = 50
    empresa_fuente: str = "Arial"
    empresa_tamaño: int = 20
    empresa_color: str = "#000000"
    empresa_negrita: bool = True
    
    mostrar_web: bool = False
    web_texto: str = ""
    web_x: int = 50
    web_y: int = 580
    web_fuente: str = "Arial"
    web_tamaño: int = 12
    web_color: str = "#0066CC"
    web_negrita: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la plantilla a un diccionario"""
        return {
            'nombre': self.nombre,
            'ancho': self.ancho,
            'alto': self.alto,
            'logo_path': self.logo_path,
            'logo_x': self.logo_x,
            'logo_y': self.logo_y,
            'logo_ancho': self.logo_ancho,
            'logo_alto': self.logo_alto,
            'fondo_color': self.fondo_color,
            'fondo_imagen_path': self.fondo_imagen_path,
            'fondo_opacidad': self.fondo_opacidad,
            'mostrar_nombre': self.mostrar_nombre,
            'nombre_x': self.nombre_x,
            'nombre_y': self.nombre_y,
            'nombre_fuente': self.nombre_fuente,
            'nombre_tamaño': self.nombre_tamaño,
            'nombre_color': self.nombre_color,
            'nombre_negrita': self.nombre_negrita,
            'mostrar_cedula': self.mostrar_cedula,
            'cedula_x': self.cedula_x,
            'cedula_y': self.cedula_y,
            'cedula_fuente': self.cedula_fuente,
            'cedula_tamaño': self.cedula_tamaño,
            'cedula_color': self.cedula_color,
            'cedula_negrita': self.cedula_negrita,
            'mostrar_cargo': self.mostrar_cargo,
            'cargo_x': self.cargo_x,
            'cargo_y': self.cargo_y,
            'cargo_fuente': self.cargo_fuente,
            'cargo_tamaño': self.cargo_tamaño,
            'cargo_color': self.cargo_color,
            'cargo_negrita': self.cargo_negrita,
            'codigo_barras_x': self.codigo_barras_x,
            'codigo_barras_y': self.codigo_barras_y,
            'codigo_barras_ancho': self.codigo_barras_ancho,
            'codigo_barras_alto': self.codigo_barras_alto,
            'mostrar_numero_codigo': self.mostrar_numero_codigo,
            'numero_codigo_fuente': self.numero_codigo_fuente,
            'numero_codigo_tamaño': self.numero_codigo_tamaño,
            'numero_codigo_color': self.numero_codigo_color,
            'mostrar_foto': self.mostrar_foto,
            'foto_x': self.foto_x,
            'foto_y': self.foto_y,
            'foto_ancho': self.foto_ancho,
            'foto_alto': self.foto_alto,
            'mostrar_empresa': self.mostrar_empresa,
            'empresa_texto': self.empresa_texto,
            'empresa_x': self.empresa_x,
            'empresa_y': self.empresa_y,
            'empresa_fuente': self.empresa_fuente,
            'empresa_tamaño': self.empresa_tamaño,
            'empresa_color': self.empresa_color,
            'empresa_negrita': self.empresa_negrita,
            'mostrar_web': self.mostrar_web,
            'web_texto': self.web_texto,
            'web_x': self.web_x,
            'web_y': self.web_y,
            'web_fuente': self.web_fuente,
            'web_tamaño': self.web_tamaño,
            'web_color': self.web_color,
            'web_negrita': self.web_negrita,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CarnetTemplate':
        """Crea una plantilla desde un diccionario"""
        return cls(**data)

