"""
Servicio de verificación OCR para carnets generados
Usa Tesseract OCR para verificar que el contenido de los carnets sea correcto
"""
import logging
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from PIL import Image
from pdf2image import convert_from_path
import re

# Importar pytesseract de forma opcional
try:
    import pytesseract
    TESSERACT_DISPONIBLE = True
    import_error = None
    
    # Configurar ruta de Tesseract automáticamente si no está en PATH
    rutas_comunes = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
    ]
    
    # Verificar si Tesseract está en PATH, si no, buscar en rutas comunes
    try:
        pytesseract.get_tesseract_version()
    except:
        # Tesseract no está en PATH, buscar en rutas comunes
        for ruta in rutas_comunes:
            if os.path.exists(ruta):
                pytesseract.pytesseract.tesseract_cmd = ruta
                break
except ImportError as e:
    pytesseract = None
    TESSERACT_DISPONIBLE = False
    import_error = e

logger = logging.getLogger(__name__)


class OCRVerifier:
    """Verificador OCR para carnets generados usando Tesseract OCR"""
    
    def __init__(self):
        """Inicializa el verificador OCR con Tesseract"""
        self._verificar_tesseract()
    
    def _verificar_tesseract(self):
        """Verifica que Tesseract esté instalado y disponible"""
        if not TESSERACT_DISPONIBLE:
            logger.warning("pytesseract no está instalado. Instala con: pip install pytesseract")
            return
        
        try:
            # Intentar obtener la versión de Tesseract
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract OCR disponible (versión {version})")
        except Exception as e:
            # Intentar configurar ruta automáticamente
            rutas_comunes = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
            ]
            
            tesseract_encontrado = False
            for ruta in rutas_comunes:
                if os.path.exists(ruta):
                    pytesseract.pytesseract.tesseract_cmd = ruta
                    try:
                        version = pytesseract.get_tesseract_version()
                        logger.info(f"Tesseract OCR encontrado y configurado automáticamente (versión {version})")
                        logger.info(f"Ruta: {ruta}")
                        tesseract_encontrado = True
                        break
                    except:
                        continue
            
            if not tesseract_encontrado:
                logger.error("=" * 60)
                logger.error("ERROR: Tesseract OCR no está instalado o no está en PATH")
                logger.error("=" * 60)
                logger.error(f"Detalle del error: {e}")
                logger.error("")
                logger.error("SOLUCIÓN REQUERIDA:")
                logger.error("1. Descarga e instala Tesseract OCR desde:")
                logger.error("   https://github.com/UB-Mannheim/tesseract/wiki")
                logger.error("   (Windows: Descarga el instalador .exe)")
                logger.error("2. Durante la instalación, asegúrate de agregar Tesseract al PATH")
                logger.error("   o configura la ruta manualmente:")
                logger.error("   pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
                logger.error("3. Instala el paquete Python: pip install pytesseract")
                logger.error("4. Reinicia la aplicación después de instalar")
                logger.error("=" * 60)
    
    def _extraer_texto_imagen(self, ruta_imagen: Path) -> str:
        """
        Extrae texto de una imagen usando Tesseract OCR
        
        Args:
            ruta_imagen: Ruta a la imagen PNG
            
        Returns:
            Texto extraído de la imagen
        """
        if not TESSERACT_DISPONIBLE:
            raise RuntimeError("Tesseract OCR no está disponible. Instala Tesseract y pytesseract.")
        
        try:
            # Abrir imagen
            imagen = Image.open(ruta_imagen)
            
            # Extraer texto con Tesseract
            # Usar español e inglés como idiomas
            texto = pytesseract.image_to_string(
                imagen,
                lang='spa+eng',  # Español e inglés
                config='--psm 6'  # Asumir un bloque uniforme de texto
            )
            
            logger.debug(f"Texto extraído de {ruta_imagen.name}: {texto[:100]}...")
            return texto.strip()
        except Exception as e:
            logger.error(f"Error al extraer texto de imagen {ruta_imagen}: {e}")
            # Si falla con español+inglés, intentar solo español
            try:
                imagen = Image.open(ruta_imagen)
                texto = pytesseract.image_to_string(imagen, lang='spa', config='--psm 6')
                return texto.strip()
            except:
                return ""
    
    def _extraer_texto_pdf(self, ruta_pdf: Path) -> str:
        """
        Extrae texto de un PDF usando Tesseract OCR
        
        Args:
            ruta_pdf: Ruta al archivo PDF
            
        Returns:
            Texto extraído del PDF
        """
        if not TESSERACT_DISPONIBLE:
            raise RuntimeError("Tesseract OCR no está disponible. Instala Tesseract y pytesseract.")
        
        try:
            # Convertir PDF a imágenes
            imagenes = convert_from_path(
                str(ruta_pdf),
                dpi=300,  # DPI alto para mejor calidad OCR
                first_page=1,
                last_page=1  # Solo la primera página
            )
            
            if not imagenes:
                return ""
            
            # Extraer texto de la primera imagen
            texto = pytesseract.image_to_string(
                imagenes[0],
                lang='spa+eng',  # Español e inglés
                config='--psm 6'
            )
            
            return texto.strip()
        except Exception as e:
            logger.error(f"Error al extraer texto de PDF {ruta_pdf}: {e}")
            # Intentar solo con español si falla
            try:
                imagenes = convert_from_path(str(ruta_pdf), dpi=300, first_page=1, last_page=1)
                if imagenes:
                    texto = pytesseract.image_to_string(imagenes[0], lang='spa', config='--psm 6')
                    return texto.strip()
            except:
                pass
            return ""
    
    def _normalizar_texto(self, texto: str) -> str:
        """
        Normaliza el texto para comparación (elimina espacios extra, convierte a mayúsculas)
        
        Args:
            texto: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        # Eliminar espacios múltiples y saltos de línea
        texto = re.sub(r'\s+', ' ', texto)
        # Convertir a mayúsculas para comparación
        texto = texto.upper().strip()
        return texto
    
    def _buscar_palabra_en_texto(self, palabra: str, texto: str, umbral_similitud: float = 0.8) -> bool:
        """
        Busca una palabra en el texto con un umbral de similitud
        
        Args:
            palabra: Palabra a buscar
            texto: Texto donde buscar
            umbral_similitud: Umbral de similitud (0.0 a 1.0)
            
        Returns:
            True si se encuentra con suficiente similitud
        """
        palabra_norm = self._normalizar_texto(palabra)
        texto_norm = self._normalizar_texto(texto)
        
        # Búsqueda exacta primero
        if palabra_norm in texto_norm:
            logger.debug(f"Encontrado exacto: '{palabra_norm}' en texto")
            return True
        
        # Para códigos cortos (como "Z00252", "22232323"), buscar sin espacios
        # El OCR a veces lee "Z 0 0 2 5 2" en lugar de "Z00252"
        palabra_sin_espacios = palabra_norm.replace(' ', '')
        texto_sin_espacios = texto_norm.replace(' ', '')
        if palabra_sin_espacios in texto_sin_espacios:
            logger.debug(f"Encontrado sin espacios: '{palabra_sin_espacios}' en texto")
            return True
        
        # Búsqueda por palabras individuales
        palabras_buscar = palabra_norm.split()
        palabras_texto = texto_norm.split()
        
        coincidencias = 0
        for palabra_buscar in palabras_buscar:
            for palabra_texto in palabras_texto:
                # Comparación simple (puedes mejorar con fuzzy matching)
                if palabra_buscar in palabra_texto or palabra_texto in palabra_buscar:
                    coincidencias += 1
                    break
        
        similitud = coincidencias / len(palabras_buscar) if palabras_buscar else 0
        
        # Para códigos alfanuméricos, ser más flexible
        if len(palabra_norm) <= 10 and any(c.isdigit() for c in palabra_norm):
            # Si es un código corto, buscar caracteres individuales
            caracteres_encontrados = sum(1 for c in palabra_sin_espacios if c in texto_sin_espacios)
            similitud_caracteres = caracteres_encontrados / len(palabra_sin_espacios) if palabra_sin_espacios else 0
            if similitud_caracteres >= 0.7:  # 70% de caracteres encontrados
                logger.debug(f"Encontrado por caracteres ({similitud_caracteres:.2f}): '{palabra_norm}'")
                return True
        
        return similitud >= umbral_similitud
    
    def verificar_carnet(
        self,
        ruta_archivo: Path,
        datos_esperados: Dict[str, str],
        umbral_similitud: float = 0.8
    ) -> Tuple[bool, str, Dict[str, bool]]:
        """
        Verifica que un carnet contenga los datos esperados
        
        Args:
            ruta_archivo: Ruta al archivo PNG o PDF del carnet
            datos_esperados: Diccionario con los datos esperados:
                - nombres: Nombre del empleado
                - apellidos: Apellidos del empleado
                - descripcion: Código de empleado
                - id_unico: ID único del código de barras
            umbral_similitud: Umbral de similitud para la verificación (0.0 a 1.0)
            
        Returns:
            Tupla (exito, mensaje, resultados_detallados)
            - exito: True si todos los datos se verificaron correctamente
            - mensaje: Mensaje descriptivo del resultado
            - resultados_detallados: Diccionario con el resultado de cada campo
        """
        if not TESSERACT_DISPONIBLE:
            return False, "Tesseract OCR no está disponible. Instala Tesseract y pytesseract.", {}
        
        if not ruta_archivo.exists():
            return False, f"Archivo no encontrado: {ruta_archivo}", {}
        
        # Extraer texto según el tipo de archivo
        try:
            if ruta_archivo.suffix.lower() == '.pdf':
                texto_extraido = self._extraer_texto_pdf(ruta_archivo)
            elif ruta_archivo.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                texto_extraido = self._extraer_texto_imagen(ruta_archivo)
            else:
                return False, f"Formato de archivo no soportado: {ruta_archivo.suffix}", {}
        except Exception as e:
            logger.error(f"Error al extraer texto: {e}")
            return False, f"Error al extraer texto: {str(e)}", {}
        
        if not texto_extraido:
            return False, "No se pudo extraer texto del archivo", {}
        
        # Logging detallado para diagnóstico
        logger.info(f"Texto completo extraído (primeros 500 caracteres): {texto_extraido[:500]}")
        logger.debug(f"Texto completo extraído: {texto_extraido}")
        logger.info(f"Datos esperados para comparar: {datos_esperados}")
        
        # Verificar cada campo esperado
        resultados = {}
        campos_faltantes = []
        campos_encontrados = []
        
        # Verificar nombres
        if 'nombres' in datos_esperados and datos_esperados['nombres']:
            encontrado = self._buscar_palabra_en_texto(
                datos_esperados['nombres'],
                texto_extraido,
                umbral_similitud
            )
            resultados['nombres'] = encontrado
            if encontrado:
                campos_encontrados.append('nombres')
                logger.info(f"✓ Nombres '{datos_esperados['nombres']}' encontrado correctamente")
            else:
                campos_faltantes.append('nombres')
                logger.warning(f"✗ Nombres '{datos_esperados['nombres']}' no encontrado en texto extraído")
        
        # Verificar apellidos
        if 'apellidos' in datos_esperados and datos_esperados['apellidos']:
            encontrado = self._buscar_palabra_en_texto(
                datos_esperados['apellidos'],
                texto_extraido,
                umbral_similitud
            )
            resultados['apellidos'] = encontrado
            if encontrado:
                campos_encontrados.append('apellidos')
                logger.info(f"✓ Apellidos '{datos_esperados['apellidos']}' encontrado correctamente")
            else:
                campos_faltantes.append('apellidos')
                logger.warning(f"✗ Apellidos '{datos_esperados['apellidos']}' no encontrado en texto extraído")
        
        # Verificar descripción (código de empleado)
        if 'descripcion' in datos_esperados and datos_esperados['descripcion']:
            encontrado = self._buscar_palabra_en_texto(
                datos_esperados['descripcion'],
                texto_extraido,
                umbral_similitud
            )
            resultados['descripcion'] = encontrado
            if encontrado:
                campos_encontrados.append('descripcion')
                logger.info(f"✓ Descripción '{datos_esperados['descripcion']}' encontrado correctamente")
            else:
                campos_faltantes.append('descripcion')
                logger.warning(f"✗ Descripción '{datos_esperados['descripcion']}' no encontrado en texto extraído")
                logger.warning(f"  Buscando: '{datos_esperados['descripcion']}' en texto: '{texto_extraido[:200]}...'")
        
        # Verificar ID único
        if 'id_unico' in datos_esperados and datos_esperados['id_unico']:
            encontrado = self._buscar_palabra_en_texto(
                datos_esperados['id_unico'],
                texto_extraido,
                umbral_similitud
            )
            resultados['id_unico'] = encontrado
            if encontrado:
                campos_encontrados.append('id_unico')
                logger.info(f"✓ ID único '{datos_esperados['id_unico']}' encontrado correctamente")
            else:
                campos_faltantes.append('id_unico')
                logger.warning(f"✗ ID único '{datos_esperados['id_unico']}' no encontrado en texto extraído")
                logger.warning(f"  Buscando: '{datos_esperados['id_unico']}' en texto: '{texto_extraido[:200]}...'")
        
        # Determinar resultado final
        if campos_faltantes:
            mensaje = f"Campos no encontrados: {', '.join(campos_faltantes)}"
            if campos_encontrados:
                mensaje += f" | Campos encontrados: {', '.join(campos_encontrados)}"
            logger.warning(f"Resumen verificación: {mensaje}")
            return False, mensaje, resultados
        
        logger.info(f"✓ Todos los campos verificados correctamente: {', '.join(campos_encontrados)}")
        return True, "Todos los campos verificados correctamente", resultados
    
    def verificar_carnets_masivos(
        self,
        rutas_archivos: List[Path],
        datos_empleados: List[Dict[str, str]],
        umbral_similitud: float = 0.8
    ) -> Dict[Path, Tuple[bool, str, Dict[str, bool]]]:
        """
        Verifica múltiples carnets en lote
        
        Args:
            rutas_archivos: Lista de rutas a los archivos de carnets
            datos_empleados: Lista de diccionarios con datos esperados para cada carnet
            umbral_similitud: Umbral de similitud para la verificación
            
        Returns:
            Diccionario con los resultados de verificación para cada archivo
        """
        resultados = {}
        
        for ruta, datos in zip(rutas_archivos, datos_empleados):
            exito, mensaje, detalles = self.verificar_carnet(
                ruta,
                datos,
                umbral_similitud
            )
            resultados[ruta] = (exito, mensaje, detalles)
        
        return resultados
