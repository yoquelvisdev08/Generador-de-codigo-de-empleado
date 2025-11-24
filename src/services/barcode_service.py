"""
Servicio para generación y validación de códigos de barras
"""
import barcode
from barcode.writer import ImageWriter
from barcode import Code128, EAN13, EAN8, Code39
from typing import Optional, Tuple, Dict
from pathlib import Path
from PIL import Image, ImageStat
from pyzbar import pyzbar
import numpy as np
import logging
import os

from config.settings import IMAGES_DIR, BARCODE_FORMATS, BARCODE_IMAGE_OPTIONS
from src.utils.file_utils import limpiar_nombre_archivo, obtener_ruta_imagen, crear_directorio_si_no_existe

logger = logging.getLogger(__name__)


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
                              nombres: Optional[str] = None,
                              apellidos: Optional[str] = None,
                              texto_debajo: Optional[str] = None,
                              tamano_fuente_texto: Optional[int] = None) -> Tuple[str, str, Path]:
        """
        Genera un código de barras y lo guarda como imagen
        
        Args:
            datos: Datos a codificar en el código de barras
            formato: Formato del código (Code128, EAN13, EAN8, Code39)
            id_unico: ID único del código (opcional)
            nombres: Nombres del empleado (opcional)
            apellidos: Apellidos del empleado (opcional)
            texto_debajo: Texto a mostrar debajo del código de barras (opcional)
            tamano_fuente_texto: Tamaño de fuente en píxeles para el texto debajo (opcional, por defecto 20)
            
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
            
            # Crear nombre completo para el archivo
            nombre_completo = f"{nombres or ''} {apellidos or ''}".strip() or "sin_nombre"
            
            ruta_imagen = obtener_ruta_imagen(
                nombre_completo,
                datos,
                self.directorio_imagenes
            )
            
            # Configurar opciones de imagen
            opciones_imagen = {**BARCODE_IMAGE_OPTIONS.copy()}
            
            # Desactivar write_text para evitar que la librería agregue el texto automáticamente
            # Lo agregaremos manualmente después para tener mejor control
            opciones_imagen['write_text'] = False
            
            # Guardar el código de barras sin texto
            codigo.save(str(ruta_imagen.with_suffix('')), options=opciones_imagen)
            
            # Asegurar que la extensión .png esté presente
            ruta_imagen_final = ruta_imagen.with_suffix('.png')
            if ruta_imagen != ruta_imagen_final:
                # Si el archivo se guardó sin extensión, renombrarlo
                temp_path = ruta_imagen.with_suffix('')
                if temp_path.exists():
                    temp_path.rename(ruta_imagen_final)
                    ruta_imagen = ruta_imagen_final
            
            # Si se proporciona texto, agregarlo manualmente con PIL para mejor control
            if texto_debajo:
                try:
                    with Image.open(ruta_imagen) as img:
                        from PIL import ImageDraw, ImageFont
                        
                        # Convertir a RGB si es necesario
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        ancho_original = img.width
                        alto_original = img.height
                        
                        # Usar el tamaño de fuente proporcionado o un valor por defecto
                        font_size = tamano_fuente_texto if tamano_fuente_texto else 50
                        
                        # Crear un draw temporal para calcular el ancho del texto
                        temp_img = Image.new('RGB', (1, 1), 'white')
                        temp_draw = ImageDraw.Draw(temp_img)
                        
                        # Intentar usar una fuente más grande y legible
                        try:
                            try:
                                font = ImageFont.truetype("arial.ttf", font_size)
                            except:
                                try:
                                    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                                except:
                                    # Si no encuentra Arial, intentar con otras fuentes comunes
                                    try:
                                        font = ImageFont.truetype("C:/Windows/Fonts/calibri.ttf", font_size)
                                    except:
                                        try:
                                            font = ImageFont.truetype("C:/Windows/Fonts/tahoma.ttf", font_size)
                                        except:
                                            font = ImageFont.load_default()
                        except:
                            font = ImageFont.load_default()
                        
                        # Calcular el ancho necesario para el texto
                        bbox_texto = temp_draw.textbbox((0, 0), texto_debajo, font=font)
                        ancho_texto = bbox_texto[2] - bbox_texto[0]
                        
                        # Agregar padding horizontal al texto (márgenes izquierdo y derecho)
                        padding_horizontal = 40
                        ancho_texto_con_padding = ancho_texto + padding_horizontal
                        
                        # Calcular el ancho final de la imagen (el mayor entre el código y el texto con padding)
                        ancho_final = max(ancho_original, ancho_texto_con_padding)
                        
                        # Calcular espacio necesario para el texto (aumentado para fuente más grande)
                        espacio_texto = max(35, font_size + 15)  # Al menos 35px o fuente + 15px
                        nueva_altura = alto_original + espacio_texto
                        
                        # Crear nueva imagen con fondo blanco (con ancho suficiente para el texto)
                        nueva_imagen = Image.new('RGB', (ancho_final, nueva_altura), 'white')
                        
                        # Centrar el código de barras horizontalmente si la imagen es más ancha
                        x_codigo = (ancho_final - ancho_original) // 2
                        nueva_imagen.paste(img, (x_codigo, 0))
                        
                        # Agregar texto debajo del código de barras
                        draw = ImageDraw.Draw(nueva_imagen)
                        
                        # Calcular posición del texto (centrado horizontalmente, cerca del código)
                        x_texto = (ancho_final - ancho_texto) // 2
                        y_texto = alto_original + 8  # Aumentado a 8px para mejor separación con fuente más grande
                        
                        # Dibujar el texto
                        draw.text((x_texto, y_texto), texto_debajo, fill='black', font=font)
                        
                        # Guardar la imagen modificada
                        nueva_imagen.save(ruta_imagen, 'PNG', optimize=True)
                        logger.debug(f"Texto agregado manualmente debajo del código de barras: '{texto_debajo}'")
                except Exception as e:
                    logger.warning(f"No se pudo agregar texto manualmente al código de barras: {e}")
                    # Continuar sin el texto si falla
            
            # Verificar integridad de la imagen guardada
            if not self._verificar_integridad_imagen(ruta_imagen):
                raise Exception("La imagen generada está corrupta o no se guardó correctamente")
            
            # Optimizar imagen automáticamente (compresión inteligente)
            self._optimizar_imagen(ruta_imagen)
            
            # Validar calidad de la imagen
            calidad_info = self._validar_calidad_imagen(ruta_imagen)
            if not calidad_info['es_valida']:
                logger.warning(f"Advertencia de calidad en imagen {ruta_imagen.name}: {calidad_info['mensaje']}")
            
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
    
    def _verificar_integridad_imagen(self, ruta_imagen: Path) -> bool:
        """
        Verifica que la imagen se haya guardado correctamente y no esté corrupta
        
        Args:
            ruta_imagen: Ruta a la imagen a verificar
            
        Returns:
            True si la imagen es válida, False en caso contrario
        """
        try:
            if not ruta_imagen.exists():
                logger.error(f"La imagen no existe: {ruta_imagen}")
                return False
            
            # Verificar que el archivo no esté vacío
            if ruta_imagen.stat().st_size == 0:
                logger.error(f"La imagen está vacía: {ruta_imagen}")
                return False
            
            # Intentar abrir y verificar la imagen
            with Image.open(ruta_imagen) as img:
                img.verify()  # Verifica que la imagen no esté corrupta
            
            # Reabrir la imagen (verify() cierra el archivo)
            with Image.open(ruta_imagen) as img:
                # Verificar dimensiones mínimas
                if img.width < 10 or img.height < 10:
                    logger.error(f"La imagen es demasiado pequeña: {img.width}x{img.height}")
                    return False
            
            logger.debug(f"Imagen verificada correctamente: {ruta_imagen.name}")
            return True
        except Exception as e:
            logger.error(f"Error al verificar integridad de imagen {ruta_imagen}: {e}")
            return False
    
    def _optimizar_imagen(self, ruta_imagen: Path, calidad: int = 95) -> bool:
        """
        Optimiza la imagen del código de barras mediante compresión inteligente
        
        Args:
            ruta_imagen: Ruta a la imagen a optimizar
            calidad: Calidad de compresión (0-100, por defecto 95)
            
        Returns:
            True si la optimización fue exitosa, False en caso contrario
        """
        try:
            if not ruta_imagen.exists():
                return False
            
            # Obtener tamaño original
            tamano_original = ruta_imagen.stat().st_size
            
            # Abrir imagen
            with Image.open(ruta_imagen) as img:
                # Convertir a RGB si es necesario (para códigos de barras en escala de grises)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Guardar con optimización
                # Usar compress_level=6 para un buen balance entre tamaño y velocidad
                img.save(
                    ruta_imagen,
                    'PNG',
                    optimize=True,
                    compress_level=6
                )
            
            # Obtener tamaño optimizado
            tamano_optimizado = ruta_imagen.stat().st_size
            reduccion = ((tamano_original - tamano_optimizado) / tamano_original) * 100
            
            if reduccion > 0:
                logger.debug(
                    f"Imagen optimizada: {ruta_imagen.name} - "
                    f"Reducción: {reduccion:.1f}% "
                    f"({tamano_original} bytes -> {tamano_optimizado} bytes)"
                )
            
            return True
        except Exception as e:
            logger.warning(f"Error al optimizar imagen {ruta_imagen}: {e}")
            return False
    
    def _validar_calidad_imagen(self, ruta_imagen: Path) -> Dict:
        """
        Valida la calidad de la imagen del código de barras
        
        Args:
            ruta_imagen: Ruta a la imagen a validar
            
        Returns:
            Diccionario con información de calidad:
            {
                'es_valida': bool,
                'mensaje': str,
                'detalles': dict con información adicional
            }
        """
        try:
            if not ruta_imagen.exists():
                return {
                    'es_valida': False,
                    'mensaje': 'La imagen no existe',
                    'detalles': {}
                }
            
            with Image.open(ruta_imagen) as img:
                # Obtener información de la imagen
                ancho, alto = img.size
                modo = img.mode
                
                # Calcular resolución efectiva (DPI aproximado basado en tamaño)
                # Los códigos de barras típicamente tienen ~300-600 píxeles de ancho
                # para una buena legibilidad
                resolucion_efectiva = ancho / 2.0  # Aproximación
                
                # Verificar contraste (importante para códigos de barras)
                if img.mode == 'RGB':
                    stat = ImageStat.Stat(img)
                    # Calcular diferencia promedio entre canales (indicador de contraste)
                    diferencia_promedio = (
                        abs(stat.mean[0] - stat.mean[1]) +
                        abs(stat.mean[1] - stat.mean[2]) +
                        abs(stat.mean[0] - stat.mean[2])
                    ) / 3
                else:
                    stat = ImageStat.Stat(img)
                    diferencia_promedio = 0
                
                # Verificar que la imagen tenga suficiente ancho para ser legible
                ancho_minimo_recomendado = 200
                if ancho < ancho_minimo_recomendado:
                    return {
                        'es_valida': False,
                        'mensaje': f'El ancho de la imagen ({ancho}px) es menor al recomendado ({ancho_minimo_recomendado}px)',
                        'detalles': {
                            'ancho': ancho,
                            'alto': alto,
                            'modo': modo,
                            'resolucion_efectiva': resolucion_efectiva
                        }
                    }
                
                # Verificar que la imagen tenga suficiente alto
                alto_minimo_recomendado = 50
                if alto < alto_minimo_recomendado:
                    return {
                        'es_valida': False,
                        'mensaje': f'El alto de la imagen ({alto}px) es menor al recomendado ({alto_minimo_recomendado}px)',
                        'detalles': {
                            'ancho': ancho,
                            'alto': alto,
                            'modo': modo,
                            'resolucion_efectiva': resolucion_efectiva
                        }
                    }
                
                # Si todo está bien
                return {
                    'es_valida': True,
                    'mensaje': 'Imagen de calidad adecuada',
                    'detalles': {
                        'ancho': ancho,
                        'alto': alto,
                        'modo': modo,
                        'resolucion_efectiva': resolucion_efectiva,
                        'tamano_archivo': ruta_imagen.stat().st_size,
                        'diferencia_contraste': diferencia_promedio
                    }
                }
        except Exception as e:
            logger.error(f"Error al validar calidad de imagen {ruta_imagen}: {e}")
            return {
                'es_valida': False,
                'mensaje': f'Error al validar calidad: {str(e)}',
                'detalles': {}
            }
    
    def obtener_informacion_imagen(self, ruta_imagen: Path) -> Optional[Dict]:
        """
        Obtiene información detallada sobre la imagen del código de barras
        
        Args:
            ruta_imagen: Ruta a la imagen
            
        Returns:
            Diccionario con información de la imagen o None si hay error
        """
        try:
            if not ruta_imagen.exists():
                return None
            
            with Image.open(ruta_imagen) as img:
                stat = os.stat(ruta_imagen)
                
                info = {
                    'ruta': str(ruta_imagen),
                    'nombre': ruta_imagen.name,
                    'tamano_archivo': stat.st_size,
                    'tamano_archivo_kb': round(stat.st_size / 1024, 2),
                    'dimensiones': {
                        'ancho': img.width,
                        'alto': img.height
                    },
                    'modo': img.mode,
                    'formato': img.format,
                    'fecha_modificacion': stat.st_mtime
                }
                
                # Agregar información de calidad si está disponible
                calidad_info = self._validar_calidad_imagen(ruta_imagen)
                if calidad_info.get('detalles'):
                    info['calidad'] = calidad_info['detalles']
                
                return info
        except Exception as e:
            logger.error(f"Error al obtener información de imagen {ruta_imagen}: {e}")
            return None

