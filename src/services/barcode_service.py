"""
Servicio para generación y validación de códigos de barras
"""
import barcode
from barcode.writer import ImageWriter
from barcode import Code128, EAN13, EAN8, Code39
from typing import Optional, Tuple
from pathlib import Path
from PIL import Image
from pyzbar import pyzbar
import numpy as np

from config.settings import IMAGES_DIR, BARCODE_FORMATS, BARCODE_IMAGE_OPTIONS
from src.utils.file_utils import limpiar_nombre_archivo, obtener_ruta_imagen, crear_directorio_si_no_existe


class BarcodeService:
    """Servicio para generar y validar códigos de barras"""
    
    FORMATOS_DISPONIBLES = {
        "Code128": Code128,
        "EAN13": EAN13,
        "EAN8": EAN8,
        "Code39": Code39
    }
    
    def __init__(self, directorio_imagenes: Optional[Path] = None):
        """
        Inicializa el servicio de códigos de barras
        
        Args:
            directorio_imagenes: Directorio donde se guardarán las imágenes. 
                               Si es None, usa el directorio por defecto
        """
        self.directorio_imagenes = directorio_imagenes or IMAGES_DIR
        crear_directorio_si_no_existe(self.directorio_imagenes)
    
    def generar_codigo_barras(self, datos: str, formato: str = "Code128",
                              id_unico: Optional[str] = None,
                              nombre_empleado: Optional[str] = None) -> Tuple[str, str, Path]:
        """
        Genera un código de barras y lo guarda como imagen
        
        Args:
            datos: Datos a codificar en el código de barras
            formato: Formato del código (Code128, EAN13, EAN8, Code39)
            id_unico: ID único del código (opcional)
            nombre_empleado: Nombre del empleado (opcional)
            
        Returns:
            Tupla con (datos, id_unico, ruta_imagen)
            
        Raises:
            ValueError: Si el formato no es soportado
            Exception: Si hay un error al generar el código
        """
        if formato not in self.FORMATOS_DISPONIBLES:
            raise ValueError(f"Formato {formato} no soportado")
        
        clase_barcode = self.FORMATOS_DISPONIBLES[formato]
        
        try:
            codigo = clase_barcode(datos, writer=ImageWriter())
            
            ruta_imagen = obtener_ruta_imagen(
                nombre_empleado or "sin_nombre",
                datos,
                self.directorio_imagenes
            )
            
            codigo.save(str(ruta_imagen.with_suffix('')), options={
                **BARCODE_IMAGE_OPTIONS,
                'text': datos
            })
            
            # Asegurar que la extensión .png esté presente
            ruta_imagen_final = ruta_imagen.with_suffix('.png')
            if ruta_imagen != ruta_imagen_final:
                # Si el archivo se guardó sin extensión, renombrarlo
                temp_path = ruta_imagen.with_suffix('')
                if temp_path.exists():
                    temp_path.rename(ruta_imagen_final)
                    ruta_imagen = ruta_imagen_final
            
            return datos, id_unico or datos, ruta_imagen
        except Exception as e:
            raise Exception(f"Error al generar código de barras: {str(e)}")
    
    def validar_codigo_barras(self, ruta_imagen: Path, valor_esperado: str) -> Tuple[bool, Optional[str]]:
        """
        Valida un código de barras leyendo la imagen y comparando con el valor esperado
        
        Args:
            ruta_imagen: Ruta a la imagen del código de barras
            valor_esperado: Valor que se espera leer del código
            
        Returns:
            Tupla con (es_valido, mensaje_error)
        """
        try:
            if not ruta_imagen.exists():
                return False, f"La imagen no existe: {ruta_imagen}"
            
            imagen = Image.open(str(ruta_imagen))
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
        """
        Valida que los datos cumplan con los requisitos del formato
        
        Args:
            datos: Datos a validar
            formato: Formato del código de barras
            
        Returns:
            Tupla con (es_valido, mensaje_error)
        """
        if not datos or not datos.strip():
            return False, "Los datos no pueden estar vacíos"
        
        if formato not in BARCODE_FORMATS:
            return False, f"Formato {formato} no reconocido"
        
        formato_info = BARCODE_FORMATS[formato]
        max_length = formato_info["max_length"]
        
        if formato in ["EAN13", "EAN8"]:
            if not datos.isdigit() or len(datos) != max_length:
                return False, f"{formato} requiere exactamente {max_length} dígitos numéricos"
        else:
            if len(datos) > max_length:
                return False, f"{formato} no puede exceder {max_length} caracteres"
        
        return True, None
    
    def obtener_formatos_disponibles(self) -> list:
        """
        Obtiene la lista de formatos disponibles
        
        Returns:
            Lista de nombres de formatos disponibles
        """
        return list(self.FORMATOS_DISPONIBLES.keys())

