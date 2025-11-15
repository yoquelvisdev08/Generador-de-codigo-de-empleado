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
        
        # Crear widget padre como ventana oculta que no aparezca en el taskbar ni en el selector de aplicaciones
        self.parent_widget = QWidget()
        # Combinar flags para ocultar completamente la ventana del sistema operativo
        self.parent_widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnBottomHint |
            Qt.WindowType.Tool |  # No aparece en el taskbar
            Qt.WindowType.BypassWindowManagerHint  # El sistema operativo lo ignora completamente
        )
        
        # Configurar atributos para que no se active ni aparezca en ningún lugar
        self.parent_widget.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.parent_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        # Establecer título vacío para que no aparezca con nombre en el selector
        self.parent_widget.setWindowTitle("")
        
        # Asegurar que no tenga focus ni aparezca en el selector
        # Qt ya está importado al inicio del archivo, no necesitamos importarlo de nuevo
        self.parent_widget.setWindowState(Qt.WindowState.WindowNoState)
        
        # Mover fuera de la pantalla visible
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            self.parent_widget.move(screen_geometry.width() + 2000, screen_geometry.height() + 2000)
        else:
            self.parent_widget.move(-20000, -20000)
        
        # Crear QWebEngineView como hijo del widget padre (antes de mostrar)
        self.web_view = QWebEngineView(self.parent_widget)
        
        # Hacer visible solo cuando sea necesario para renderizar (pero no aparecerá en el selector)
        # El widget se mostrará solo durante el renderizado y luego se ocultará
        self.parent_widget.show()
        self.parent_widget.lower()
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
            es_primer_renderizado = not self._inicializado
            if not self._inicializado:
                if not self._inicializar_widgets():
                    return None
                
                # Si es el primer renderizado, hacer un renderizado de prueba para inicializar completamente el widget
                # Esto es crítico para evitar imágenes en blanco en el primer intento
                if es_primer_renderizado:
                    logger.info("Primer renderizado detectado, realizando renderizado de prueba...")
                    # Esperar un momento para que el widget se inicialice completamente
                    QTimer.singleShot(500, lambda: None)
                    QApplication.processEvents()
                    
                    # Hacer un renderizado de prueba con HTML simple para inicializar el motor
                    html_prueba = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { margin: 0; padding: 0; background: white; }
                            div { width: 100px; height: 100px; background: #f0f0f0; }
                        </style>
                    </head>
                    <body>
                        <div></div>
                    </body>
                    </html>
                    """
                    
                    # Renderizar HTML de prueba en tamaño pequeño
                    web_view_temp = self.web_view
                    parent_widget_temp = self.parent_widget
                    
                    parent_widget_temp.setFixedSize(100, 100)
                    web_view_temp.setFixedSize(100, 100)
                    web_view_temp.setZoomFactor(1.0)
                    parent_widget_temp.show()
                    web_view_temp.show()
                    QApplication.processEvents()
                    
                    # Cargar HTML de prueba
                    loop_prueba = QEventLoop()
                    cargado_prueba = False
                    
                    def on_load_finished_prueba(ok):
                        nonlocal cargado_prueba
                        if ok:
                            cargado_prueba = True
                        loop_prueba.quit()
                    
                    web_view_temp.loadFinished.connect(on_load_finished_prueba)
                    web_view_temp.setHtml(html_prueba, baseUrl=QUrl("file:///"))
                    
                    timer_prueba = QTimer()
                    timer_prueba.timeout.connect(loop_prueba.quit)
                    timer_prueba.setSingleShot(True)
                    timer_prueba.start(3000)
                    
                    loop_prueba.exec()
                    timer_prueba.stop()
                    
                    # Esperar un momento adicional después del renderizado de prueba
                    QTimer.singleShot(500, lambda: None)
                    QApplication.processEvents()
                    
                    logger.info("Renderizado de prueba completado, widget inicializado")
            
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
            
            # Asegurar que estén visibles para el renderizado (pero no aparecerán en el selector)
            # Los flags ya están configurados para ocultarlo del sistema operativo
            parent_widget.show()
            parent_widget.lower()
            web_view.show()
            
            # Procesar eventos para que se actualice el tamaño
            QApplication.processEvents()
            
            # Esperar un momento para asegurar que el widget esté completamente inicializado
            QTimer.singleShot(100, lambda: None)
            QApplication.processEvents()
            
            # Cargar HTML después de establecer el zoom
            logger.debug(f"Renderizando HTML: widget {ancho_render}x{alto_render}, HTML base {ancho}x{alto}, DPI: {dpi}, zoom: {web_view.zoomFactor()}")
            web_view.setHtml(html_content, baseUrl=QUrl("file:///"))
            
            # Esperar a que cargue completamente usando un loop de eventos
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
            
            # Timeout de seguridad (aumentado a 5s para dar más tiempo al primer renderizado)
            timer = QTimer()
            timer.timeout.connect(loop.quit)
            timer.setSingleShot(True)
            timer.start(5000)
            
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
            
            # Esperar renderizado completo (aumentado significativamente para asegurar que todo esté renderizado)
            # Si es el primer renderizado, esperar más tiempo
            iteraciones_espera = 6 if es_primer_renderizado else 5
            tiempo_espera = 1200 if es_primer_renderizado else 1000
            
            logger.debug(f"Esperando renderizado completo: {iteraciones_espera} iteraciones de {tiempo_espera}ms")
            
            for i in range(iteraciones_espera):
                QApplication.processEvents()
                QTimer.singleShot(tiempo_espera, lambda: None)
                QApplication.processEvents()
                # Forzar actualización en cada iteración
                web_view.update()
                web_view.repaint()
                QApplication.processEvents()
            
            # Forzar actualización del widget múltiples veces
            for _ in range(3):
                web_view.update()
                web_view.repaint()
                QApplication.processEvents()
                QTimer.singleShot(200, lambda: None)
                QApplication.processEvents()
            
            # Esperar un momento adicional para asegurar renderizado completo
            # Más tiempo si es el primer renderizado
            tiempo_adicional = 1200 if es_primer_renderizado else 800
            QTimer.singleShot(tiempo_adicional, lambda: None)
            QApplication.processEvents()
            
            # Verificar estabilidad del renderizado comparando dos capturas consecutivas
            # Si las capturas son idénticas, el renderizado está estable
            logger.debug("Verificando estabilidad del renderizado...")
            captura_anterior = None
            intentos_estabilidad = 0
            max_intentos_estabilidad = 3
            
            while intentos_estabilidad < max_intentos_estabilidad:
                QApplication.processEvents()
                captura_actual = web_view.grab()
                
                if captura_anterior is not None and not captura_anterior.isNull() and not captura_actual.isNull():
                    # Comparar las dos capturas
                    img_anterior = captura_anterior.toImage()
                    img_actual = captura_actual.toImage()
                    
                    if img_anterior.size() == img_actual.size():
                        # Comparar algunos píxeles aleatorios para verificar estabilidad
                        puntos_muestra = [
                            (ancho_render // 4, alto_render // 4),
                            (ancho_render // 2, alto_render // 2),
                            (3 * ancho_render // 4, 3 * alto_render // 4)
                        ]
                        
                        estable = True
                        for x, y in puntos_muestra:
                            if x < img_anterior.width() and y < img_anterior.height():
                                color_anterior = img_anterior.pixelColor(x, y)
                                color_actual = img_actual.pixelColor(x, y)
                                if color_anterior != color_actual:
                                    estable = False
                                    break
                        
                        if estable:
                            logger.debug("Renderizado estable detectado")
                            break
                
                captura_anterior = captura_actual
                intentos_estabilidad += 1
                
                if intentos_estabilidad < max_intentos_estabilidad:
                    QTimer.singleShot(500, lambda: None)
                    QApplication.processEvents()
                    web_view.update()
                    web_view.repaint()
                    QApplication.processEvents()
            
            logger.debug(f"Verificación de estabilidad completada después de {intentos_estabilidad + 1} intentos")
            
            # Capturar imagen con verificación de que no esté en blanco
            # Aumentar número de intentos para dar más oportunidades
            max_intentos = 5
            imagen = None
            
            for intento in range(max_intentos):
                QApplication.processEvents()
                
                # Esperar un momento antes de cada captura para asegurar que el renderizado esté completo
                if intento > 0:
                    tiempo_antes_captura = 800 if intento == 1 else 600
                    QTimer.singleShot(tiempo_antes_captura, lambda: None)
                    QApplication.processEvents()
                    web_view.update()
                    web_view.repaint()
                    QApplication.processEvents()
                
                imagen = web_view.grab()
                
                if imagen.isNull():
                    logger.warning(f"Captura {intento + 1} falló, reintentando...")
                    QTimer.singleShot(800, lambda: None)
                    QApplication.processEvents()
                    continue
                
                # Verificar que la imagen no esté completamente en blanco
                qimage_temp = imagen.toImage()
                if not qimage_temp.isNull():
                    # Verificar más píxeles distribuidos por toda la imagen para asegurar que tenga contenido
                    puntos_verificacion = [
                        (10, 10),
                        (ancho_render // 4, alto_render // 4),
                        (ancho_render // 2, alto_render // 2),
                        (3 * ancho_render // 4, 3 * alto_render // 4),
                        (max(10, ancho_render - 10), max(10, alto_render - 10))
                    ]
                    
                    sample_pixels = []
                    for x, y in puntos_verificacion:
                        if x < qimage_temp.width() and y < qimage_temp.height():
                            pixel = qimage_temp.pixelColor(x, y)
                            if pixel.isValid():
                                sample_pixels.append(pixel)
                    
                    # Verificar que no todos los píxeles sean blancos
                    all_white = len(sample_pixels) > 0 and all(
                        p.red() >= 250 and p.green() >= 250 and p.blue() >= 250 
                        for p in sample_pixels
                    )
                    
                    if all_white and ancho_render > 100 and alto_render > 100:
                        logger.warning(f"Captura {intento + 1} parece estar en blanco, reintentando...")
                        if intento < max_intentos - 1:
                            # Esperar más tiempo entre reintentos, especialmente en los primeros intentos
                            tiempo_reintento = 2000 if intento == 0 else (1500 if intento == 1 else 1000)
                            QTimer.singleShot(tiempo_reintento, lambda: None)
                            QApplication.processEvents()
                            # Forzar actualización múltiple antes del siguiente intento
                            for _ in range(3):
                                web_view.update()
                                web_view.repaint()
                                QApplication.processEvents()
                            continue
                    else:
                        # La imagen tiene contenido, verificar que sea estable
                        logger.debug(f"Captura {intento + 1} tiene contenido, verificando estabilidad...")
                        # Hacer una segunda captura rápida para verificar estabilidad
                        QTimer.singleShot(300, lambda: None)
                        QApplication.processEvents()
                        imagen_verificacion = web_view.grab()
                        
                        if not imagen_verificacion.isNull():
                            # Comparar algunos píxeles clave entre las dos capturas
                            img_verif = imagen_verificacion.toImage()
                            estable = True
                            
                            for x, y in puntos_verificacion[:3]:  # Solo verificar 3 puntos para velocidad
                                if x < qimage_temp.width() and y < qimage_temp.height() and x < img_verif.width() and y < img_verif.height():
                                    color1 = qimage_temp.pixelColor(x, y)
                                    color2 = img_verif.pixelColor(x, y)
                                    if color1 != color2:
                                        estable = False
                                        break
                            
                            if estable:
                                logger.debug("Imagen estable confirmada")
                                break
                            else:
                                logger.debug("Imagen aún no estable, continuando espera...")
                                if intento < max_intentos - 1:
                                    QTimer.singleShot(500, lambda: None)
                                    QApplication.processEvents()
                                    continue
                        else:
                            # Si la verificación falla, usar la imagen original
                            break
                else:
                    logger.warning(f"QImage temporal es nula en intento {intento + 1}")
                    if intento < max_intentos - 1:
                        QTimer.singleShot(800, lambda: None)
                        QApplication.processEvents()
                        continue
            
            if imagen is None or imagen.isNull():
                logger.error("No se pudo capturar la imagen del QWebEngineView después de múltiples intentos")
                return None
            
            logger.debug(f"Imagen capturada: {imagen.width()}x{imagen.height()}")
            
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

