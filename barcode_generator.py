import barcode
from barcode.writer import ImageWriter
from barcode import Code128, EAN13, EAN8, Code39
import uuid
import os
from typing import Optional, Tuple
from PIL import Image
from pyzbar import pyzbar
import numpy as np


class GeneradorCodigoBarras:
    FORMATOS_DISPONIBLES = {
        "Code128": Code128,
        "EAN13": EAN13,
        "EAN8": EAN8,
        "Code39": Code39
    }
    
    def __init__(self, directorio_imagenes: str = "codigos_generados"):
        self.directorio_imagenes = directorio_imagenes
        self.crear_directorio()
    
    def crear_directorio(self):
        if not os.path.exists(self.directorio_imagenes):
            os.makedirs(self.directorio_imagenes)
    
    def generar_id_unico(self) -> str:
        return str(uuid.uuid4())
    
    def limpiar_nombre_archivo(self, nombre: str) -> str:
        caracteres_invalidos = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        nombre_limpio = nombre
        for char in caracteres_invalidos:
            nombre_limpio = nombre_limpio.replace(char, '_')
        return nombre_limpio.strip()
    
    def generar_codigo_barras(self, datos: str, formato: str = "Code128",
                              id_unico: Optional[str] = None,
                              nombre_empleado: Optional[str] = None) -> Tuple[str, str, str]:
        if formato not in self.FORMATOS_DISPONIBLES:
            raise ValueError(f"Formato {formato} no soportado")
        
        if id_unico is None:
            id_unico = self.generar_id_unico()
        
        clase_barcode = self.FORMATOS_DISPONIBLES[formato]
        
        try:
            codigo = clase_barcode(datos, writer=ImageWriter())
            
            nombre_empleado_limpio = self.limpiar_nombre_archivo(nombre_empleado or "sin_nombre")
            nombre_archivo = f"{nombre_empleado_limpio}_{datos}"
            ruta_completa = os.path.join(self.directorio_imagenes, nombre_archivo)
            
            codigo.save(ruta_completa, options={
                'format': 'PNG',
                'module_width': 0.5,
                'module_height': 15,
                'quiet_zone': 6.5,
                'font_size': 10,
                'text_distance': 5.0,
                'background': 'white',
                'foreground': 'black',
                'write_text': True,
                'text': datos
            })
            
            ruta_imagen = f"{ruta_completa}.png"
            
            return datos, id_unico, ruta_imagen
        except Exception as e:
            raise Exception(f"Error al generar código de barras: {str(e)}")
    
    def validar_codigo_barras(self, ruta_imagen: str, valor_esperado: str) -> Tuple[bool, Optional[str]]:
        try:
            imagen = Image.open(ruta_imagen)
            imagen_array = np.array(imagen)
            
            codigos_leidos = pyzbar.decode(imagen_array)
            
            if not codigos_leidos:
                return False, "No se pudo leer el código de barras desde la imagen generada"
            
            valor_leido = codigos_leidos[0].data.decode('utf-8')
            
            if valor_leido != valor_esperado:
                return False, f"El código leído ({valor_leido}) no coincide con el ID esperado ({valor_esperado})"
            
            return True, None
        except Exception as e:
            return False, f"Error al validar el código de barras: {str(e)}"
    
    def validar_datos_formato(self, datos: str, formato: str) -> Tuple[bool, Optional[str]]:
        if not datos or not datos.strip():
            return False, "Los datos no pueden estar vacíos"
        
        if formato == "EAN13":
            if not datos.isdigit() or len(datos) != 13:
                return False, "EAN13 requiere exactamente 13 dígitos"
        elif formato == "EAN8":
            if not datos.isdigit() or len(datos) != 8:
                return False, "EAN8 requiere exactamente 8 dígitos"
        elif formato == "Code39":
            if len(datos) > 43:
                return False, "Code39 no puede exceder 43 caracteres"
        elif formato == "Code128":
            if len(datos) > 80:
                return False, "Code128 no puede exceder 80 caracteres"
        
        return True, None
    
    def obtener_formatos_disponibles(self) -> list:
        return list(self.FORMATOS_DISPONIBLES.keys())

