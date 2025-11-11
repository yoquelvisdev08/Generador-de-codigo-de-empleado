"""
Modelo de datos para códigos de barras
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class BarcodeModel:
    """Modelo de datos para representar un código de barras"""
    
    id: Optional[int] = None
    codigo_barras: str = ""
    id_unico: str = ""
    fecha_creacion: Optional[str] = None
    nombre_empleado: Optional[str] = None
    descripcion: Optional[str] = None
    formato: str = "Code128"
    nombre_archivo: Optional[str] = None
    
    @classmethod
    def from_tuple(cls, data: tuple) -> 'BarcodeModel':
        """
        Crea un BarcodeModel desde una tupla de la base de datos
        
        Args:
            data: Tupla con los datos (id, codigo_barras, id_unico, fecha_creacion,
                  nombre_empleado, descripcion, formato, nombre_archivo)
                  
        Returns:
            Instancia de BarcodeModel
        """
        if len(data) == 8:
            return cls(
                id=data[0],
                codigo_barras=data[1],
                id_unico=data[2],
                fecha_creacion=data[3],
                nombre_empleado=data[4],
                descripcion=data[5],
                formato=data[6],
                nombre_archivo=data[7]
            )
        elif len(data) == 7:
            return cls(
                id=data[0],
                codigo_barras=data[1],
                id_unico=data[2],
                fecha_creacion=data[3],
                nombre_empleado=data[4],
                descripcion=data[5],
                formato=data[6]
            )
        else:
            raise ValueError(f"Tupla de datos inválida: {len(data)} elementos")
    
    def to_dict(self) -> dict:
        """
        Convierte el modelo a un diccionario
        
        Returns:
            Diccionario con los datos del modelo
        """
        return {
            'id': self.id,
            'codigo_barras': self.codigo_barras,
            'id_unico': self.id_unico,
            'fecha_creacion': self.fecha_creacion,
            'nombre_empleado': self.nombre_empleado,
            'descripcion': self.descripcion,
            'formato': self.formato,
            'nombre_archivo': self.nombre_archivo
        }

