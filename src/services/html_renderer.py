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
        self.parent_widget = None
        self.loop = None
        self._inicializado = False
    
    def _inicializar_widgets(self):
        """Inicializa los widgets reutilizables una sola vez"""
        if self._inicializado:
            return True
        
        from PyQt6.QtWidgets import QApplication, QWidget
        
        app = QApplication.instance()
        if app is None:
            logger.error("No hay instancia de QApplication")
            return False
        
        # Crear widget padre como ventana independiente pero fuera de la pantalla
        self.parent_widget = QWidget()
        self.parent_widget.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnBottomHint)
        
        # Mover fuera de la pantalla visible
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            self.parent_widget.move(screen_geometry.width() + 2000, screen_geometry.height() + 2000)
        else:
            self.parent_widget.move(-20000, -20000)
        
        # Hacer visible (pero fuera de la vista del usuario)
        self.parent_widget.show()
        self.parent_widget.lower()
        
        # Crear QWebEngineView como hijo del widget padre
        self.web_view = QWebEngineView(self.parent_widget)
        self.web_view.show()
        
        # Configurar para renderizado de alta calidad (solo una vez)
        settings = self.web_view.settings()
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)
        
        # Deshabilitar scrollbars
        page_settings = self.web_view.page().settings()
        page_settings.setAttribute(page_settings.WebAttribute.ShowScrollBars, False)
        
        # Habilitar aceleración de hardware
        settings.setAttribute(settings.WebAttribute.Accelerated2dCanvasEnabled, True)
        try:
            settings.setAttribute(settings.WebAttribute.LocalFontsEnabled, True)
        except AttributeError:
            logger.debug("LocalFontsEnabled no está disponible en esta versión de PyQt6")
        
        self._inicializado = True
        logger.info("Widgets de renderizado inicializados (reutilizables)")
        return True
    
    def renderizar_html_a_imagen(
        self,
        html_content: str,
        ancho: int,
        alto: int,
        dpi: int = 600
    ) -> Optional[Image.Image]:
        """
        Renderiza HTML a una imagen PIL (optimizado: reutiliza QWebEngineView)
        
        Args:
            html_content: Contenido HTML a renderizar
            ancho: Ancho en píxeles (a 300 DPI)
            alto: Alto en píxeles (a 300 DPI)
            dpi: DPI para el renderizado
            
        Returns:
            Imagen PIL o None si hay error
        """
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QEventLoop, QTimer
        
        try:
            # Obtener la aplicación actual
            app = QApplication.instance()
            if app is None:
                logger.error("No hay instancia de QApplication")
                return None
            
            # Inicializar widgets reutilizables si no están inicializados
            if not self._inicializado:
                if not self._inicializar_widgets():
                    return None
            
            # Reutilizar widgets existentes
            web_view = self.web_view
            parent_widget = self.parent_widget
            
            # Calcular factor de escala si se necesita mayor DPI
            factor_escala = dpi / 300.0 if dpi > 300 else 1.0
            
            # Calcular dimensiones de renderizado
            if dpi > 300:
                ancho_render = int(ancho * factor_escala)
                alto_render = int(alto * factor_escala)
            else:
                ancho_render = ancho
                alto_render = alto
            
            # Ajustar tamaño de widgets (reutilizando los existentes)
            parent_widget.setFixedSize(ancho_render, alto_render)
            web_view.setFixedSize(ancho_render, alto_render)
            web_view.setZoomFactor(factor_escala)
            
            # Asegurar que estén visibles
            parent_widget.show()
            parent_widget.lower()
            web_view.show()
            
            # Procesar eventos para que se actualice el tamaño
            QApplication.processEvents()
            
            # Cargar HTML después de establecer el zoom
            logger.debug(f"Renderizando HTML: widget {ancho_render}x{alto_render}, HTML base {ancho}x{alto}, DPI: {dpi}, zoom: {web_view.zoomFactor()}")
            web_view.setHtml(html_content, baseUrl=QUrl("file:///"))
            
            # Esperar a que cargue completamente usando un loop de eventos (optimizado)
            loop = QEventLoop()
            cargado = False
            error_carga = False
            
            def on_load_finished(ok):
                nonlocal cargado, error_carga
                if ok:
                    cargado = True
                else:
                    error_carga = True
                loop.quit()
            
            # Desconectar señales anteriores para evitar múltiples llamadas
            try:
                web_view.loadFinished.disconnect()
            except:
                pass
            
            web_view.loadFinished.connect(on_load_finished)
            
            # Timeout de seguridad (reducido de 5s a 3s)
            timer = QTimer()
            timer.timeout.connect(loop.quit)
            timer.setSingleShot(True)
            timer.start(3000)
            
            # Ejecutar loop de eventos
            loop.exec()
            timer.stop()
            
            # Si no se cargó correctamente, retornar None
            if error_carga:
                logger.error("Error al cargar el HTML")
                return None
            if not cargado:
                logger.warning("El HTML no se cargó correctamente dentro del timeout")
                return None
            
            # Esperar renderizado (optimizado: reducido de 5 intentos de 1.5s a 2 intentos de 0.5s)
            for i in range(2):
                QApplication.processEvents()
                QTimer.singleShot(500, lambda: None)
                QApplication.processEvents()
            
            # Forzar actualización del widget
            web_view.update()
            web_view.repaint()
            QApplication.processEvents()
            
            # Capturar imagen (optimizado: menos verificaciones redundantes)
            QApplication.processEvents()
            imagen = web_view.grab()
            
            if imagen.isNull():
                logger.warning("Primera captura falló, reintentando...")
                QApplication.processEvents()
                QTimer.singleShot(300, lambda: None)
                QApplication.processEvents()
                imagen = web_view.grab()
                
                if imagen.isNull():
                    logger.error("No se pudo capturar la imagen del QWebEngineView")
                    return None
            
            logger.debug(f"Imagen capturada: {imagen.width()}x{imagen.height()}")
            
            # Verificar que la imagen no esté completamente en blanco
            qimage_temp = imagen.toImage()
            if not qimage_temp.isNull():
                # Verificar algunos píxeles para asegurar que no esté en blanco
                sample_pixels = [
                    qimage_temp.pixelColor(0, 0),
                    qimage_temp.pixelColor(ancho // 2, alto // 2),
                    qimage_temp.pixelColor(ancho - 1, alto - 1)
                ]
                all_white = all(
                    p.red() == 255 and p.green() == 255 and p.blue() == 255 
                    for p in sample_pixels
                )
                if all_white and ancho > 100 and alto > 100:
                    logger.warning("La imagen capturada parece estar completamente en blanco")
            
            # Convertir QPixmap a QImage
            qimage = imagen.toImage()
            
            if qimage.isNull():
                logger.warning("La QImage es nula")
                return None
            
            # Obtener dimensiones capturadas
            width_capturado = qimage.width()
            height_capturado = qimage.height()
            
            # Normalizar la imagen capturada al tamaño esperado
            # Esto maneja casos donde devicePixelRatio puede afectar el tamaño
            # Si el widget fue renderizado a alta resolución, la imagen debería ser del tamaño renderizado
            if width_capturado != ancho_render or height_capturado != alto_render:
                logger.info(f"Normalizando imagen capturada de {width_capturado}x{height_capturado} a {ancho_render}x{alto_render}")
                qimage = qimage.scaled(
                    ancho_render, alto_render,
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
            
            # La imagen ya está renderizada a la resolución correcta usando zoom nativo
            logger.debug(f"HTML renderizado exitosamente: {pil_image.size[0]}x{pil_image.size[1]} píxeles a {dpi} DPI")
            return pil_image
            
        except Exception as e:
            logger.error(f"Error al renderizar HTML: {e}", exc_info=True)
            return None
        # NOTA: No eliminamos los widgets aquí, se reutilizan para el siguiente renderizado
    
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
            if key in ["foto", "codigo_barras", "logo"] and not value:
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

