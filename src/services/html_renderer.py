"""
Servicio para renderizar HTML a imagen usando QWebEngineView
"""
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer, QSize, QEventLoop, pyqtSignal, QObject, Qt
from PyQt6.QtGui import QImage, QPainter
from PIL import Image
import logging
import json
import base64

logger = logging.getLogger(__name__)


class HTMLRenderer(QObject):
    """Servicio para renderizar HTML a imagen"""
    
    finished = pyqtSignal(QImage)
    
    def __init__(self):
        """Inicializa el renderizador HTML"""
        super().__init__()
        self.web_view = None
        self.loop = None
    
    def renderizar_html_a_imagen(
        self,
        html_content: str,
        ancho: int,
        alto: int,
        dpi: int = 300
    ) -> Optional[Image.Image]:
        """
        Renderiza HTML a una imagen PIL
        
        Args:
            html_content: Contenido HTML a renderizar
            ancho: Ancho en píxeles (a 300 DPI)
            alto: Alto en píxeles (a 300 DPI)
            dpi: DPI para el renderizado
            
        Returns:
            Imagen PIL o None si hay error
        """
        from PyQt6.QtWidgets import QApplication, QWidget
        from PyQt6.QtCore import QEventLoop, QTimer
        
        web_view = None
        parent_widget = None
        try:
            # Obtener la aplicación actual
            app = QApplication.instance()
            if app is None:
                logger.error("No hay instancia de QApplication")
                return None
            
            # Crear un widget padre invisible para el QWebEngineView
            parent_widget = QWidget()
            parent_widget.setFixedSize(ancho, alto)
            parent_widget.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
            parent_widget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
            
            # Crear QWebEngineView como hijo del widget padre
            web_view = QWebEngineView(parent_widget)
            web_view.setFixedSize(ancho, alto)
            web_view.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
            web_view.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
            
            # Configurar para renderizado de alta calidad
            settings = web_view.settings()
            settings.setAttribute(settings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)
            
            # Cargar HTML
            logger.info(f"Cargando HTML en QWebEngineView (tamaño: {ancho}x{alto})")
            web_view.setHtml(html_content)
            
            # Esperar a que cargue completamente usando un loop de eventos
            loop = QEventLoop()
            cargado = False
            error_carga = False
            
            def on_load_finished(ok):
                nonlocal cargado, error_carga
                if ok:
                    cargado = True
                    logger.info("HTML cargado exitosamente")
                else:
                    error_carga = True
                    logger.warning("Error al cargar HTML en QWebEngineView")
                loop.quit()
            
            web_view.loadFinished.connect(on_load_finished)
            
            # Timeout de seguridad
            timer = QTimer()
            timer.timeout.connect(loop.quit)
            timer.setSingleShot(True)
            timer.start(5000)  # 5 segundos de timeout
            
            # Ejecutar loop de eventos
            loop.exec()
            
            # Si no se cargó correctamente, retornar None
            if error_carga:
                logger.error("Error al cargar el HTML")
                return None
            if not cargado:
                logger.warning("El HTML no se cargó correctamente dentro del timeout")
                return None
            
            # Esperar un poco más para que se renderice completamente
            # Usar un segundo loop para esperar el renderizado
            loop2 = QEventLoop()
            timer2 = QTimer()
            timer2.timeout.connect(loop2.quit)
            timer2.setSingleShot(True)
            timer2.start(2000)  # Esperar 2 segundos para renderizado
            loop2.exec()
            
            # Procesar eventos finales
            QApplication.processEvents()
            
            # Renderizar a imagen
            logger.info("Capturando imagen del QWebEngineView...")
            imagen = web_view.grab()
            
            if imagen.isNull():
                logger.error("No se pudo capturar la imagen del QWebEngineView (QPixmap es nulo)")
                return None
            
            logger.info(f"Imagen capturada (antes de escalar): {imagen.width()}x{imagen.height()}")
            
            # Convertir QPixmap a QImage
            qimage = imagen.toImage()
            
            if qimage.isNull():
                logger.warning("La QImage es nula")
                return None
            
            # Obtener dimensiones capturadas
            width_capturado = qimage.width()
            height_capturado = qimage.height()
            
            # Escalar al tamaño deseado si es necesario (puede estar a 2x por devicePixelRatio)
            if width_capturado != ancho or height_capturado != alto:
                logger.info(f"Escalando imagen de {width_capturado}x{height_capturado} a {ancho}x{alto}")
                qimage = qimage.scaled(
                    ancho, alto,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            
            width = qimage.width()
            height = qimage.height()
            
            if width == 0 or height == 0:
                logger.warning(f"Dimensiones inválidas: {width}x{height}")
                return None
            
            ptr = qimage.bits()
            if ptr is None:
                logger.warning("No se pudo obtener los bits de la imagen")
                return None
                
            ptr.setsize(qimage.sizeInBytes())
            arr = ptr.asarray(width * height * 4)
            
            # Convertir RGBA a RGB usando frombytes (más compatible)
            try:
                # Convertir array a bytes
                if hasattr(arr, 'tobytes'):
                    arr_bytes = arr.tobytes()
                else:
                    arr_bytes = bytes(arr)
                
                pil_image = Image.frombytes(
                    "RGBA", (width, height), arr_bytes, "raw", "BGRA", 0, 1
                ).convert("RGB")
            except Exception as e:
                logger.warning(f"Error al convertir con frombytes, usando fallback: {e}")
                # Fallback para versiones antiguas de PIL
                try:
                    pil_image = Image.frombuffer(
                        "RGBA", (width, height), arr, "raw", "BGRA", 0, 1
                    ).convert("RGB")
                except Exception as e2:
                    logger.error(f"Error al convertir imagen: {e2}")
                    return None
            
            logger.info(f"HTML renderizado exitosamente: {width}x{height}")
            return pil_image
            
        except Exception as e:
            logger.error(f"Error al renderizar HTML: {e}", exc_info=True)
            return None
        finally:
            if web_view:
                web_view.deleteLater()
            if parent_widget:
                parent_widget.deleteLater()
    
    def renderizar_html_desde_archivo(
        self,
        ruta_html: Path,
        variables: Dict[str, Any],
        ancho: int,
        alto: int,
        dpi: int = 300
    ) -> Optional[Image.Image]:
        """
        Renderiza HTML desde archivo con variables inyectadas
        
        Args:
            ruta_html: Ruta al archivo HTML
            variables: Diccionario con variables para inyectar
            ancho: Ancho en píxeles
            alto: Alto en píxeles
            dpi: DPI para renderizado
            
        Returns:
            Imagen PIL o None si hay error
        """
        try:
            # Leer HTML
            html_content = ruta_html.read_text(encoding='utf-8')
            
            # Inyectar variables
            html_content = self._inyectar_variables(html_content, variables)
            
            # Renderizar
            return self.renderizar_html_a_imagen(html_content, ancho, alto, dpi)
            
        except Exception as e:
            logger.error(f"Error al renderizar HTML desde archivo: {e}")
            return None
    
    def _inyectar_variables(self, html: str, variables: Dict[str, Any]) -> str:
        """
        Inyecta variables en el HTML usando sintaxis {{variable}}
        
        Args:
            html: Contenido HTML
            variables: Diccionario con variables
            
        Returns:
            HTML con variables reemplazadas
        """
        import html as html_escape
        
        # Reemplazar variables {{variable}}
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            if value is None:
                value = ""
            elif isinstance(value, Path):
                # Si es una ruta de imagen, convertir a base64
                if value.exists() and value.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
                    value = self._imagen_a_base64(value)
                else:
                    # Si no existe, usar placeholder transparente para evitar errores
                    value = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            else:
                value = str(value)
            
            # Para atributos src de imágenes, usar placeholder si está vacío
            if key in ["foto", "codigo_barras"] and not value:
                value = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            
            # Escapar HTML para evitar problemas con JavaScript
            # Pero no escapar si es una URL de imagen base64
            if value.startswith("data:image"):
                # Es una imagen base64, no escapar
                html = html.replace(placeholder, value)
            else:
                # Escapar caracteres especiales HTML
                value_escaped = html_escape.escape(value)
                html = html.replace(placeholder, value_escaped)
        
        return html
    
    def _imagen_a_base64(self, ruta_imagen: Path) -> str:
        """
        Convierte una imagen a base64 para usar en HTML
        
        Args:
            ruta_imagen: Ruta a la imagen
            
        Returns:
            String base64 de la imagen
        """
        try:
            import base64
            with open(ruta_imagen, 'rb') as f:
                imagen_bytes = f.read()
                base64_str = base64.b64encode(imagen_bytes).decode('utf-8')
                extension = ruta_imagen.suffix.lower().replace('.', '')
                if extension == 'jpg':
                    extension = 'jpeg'
                return f"data:image/{extension};base64,{base64_str}"
        except Exception as e:
            logger.error(f"Error al convertir imagen a base64: {e}")
            return ""

