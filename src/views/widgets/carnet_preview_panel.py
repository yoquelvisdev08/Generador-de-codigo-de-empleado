"""
Panel de vista previa del carnet
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QApplication, QPushButton, QHBoxLayout, QColorDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QColor
from PIL import Image
from pathlib import Path
import io


class CarnetPreviewPanel(QWidget):
    """Panel para mostrar la vista previa del carnet"""
    
    def __init__(self, parent=None):
        """
        Inicializa el panel de vista previa
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.imagen_actual = None
        self.web_view = None  # QWebEngineView para mostrar HTML directamente
        self.usando_html = False  # Flag para saber si estamos usando HTML o imagen
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.setLayout(layout)
        
        # Título
        titulo = QLabel("Vista Previa del Carnet (Tamaño Real)")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        layout.addWidget(titulo)
        
        # Controles de fondo de vista previa
        layout_controles_fondo = QHBoxLayout()
        label_fondo = QLabel("Fondo de vista previa:")
        self.boton_color_fondo = QPushButton("Seleccionar Color")
        self.boton_color_fondo.setStyleSheet("background-color: #6c757d; color: white; padding: 5px;")
        self.boton_color_fondo.clicked.connect(self._seleccionar_color_fondo)
        self.color_fondo_actual = "#ffffff"  # Blanco por defecto
        layout_controles_fondo.addWidget(label_fondo)
        layout_controles_fondo.addWidget(self.boton_color_fondo)
        layout_controles_fondo.addStretch()
        layout.addLayout(layout_controles_fondo)
        
        # Área de scroll para la vista previa (sin scrollbars cuando se usa HTML)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setStyleSheet(f"background-color: {self.color_fondo_actual};")
        # Deshabilitar scrollbars por defecto (se habilitarán solo si es necesario)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Contenedor para la vista previa (puede ser QLabel o QWebEngineView)
        self.container_widget = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_widget.setLayout(container_layout)
        
        # Label para mostrar la imagen (modo PIL)
        self.label_preview = QLabel()
        self.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Tamaño real en pantalla: 54mm x 85.6mm a 96 DPI (tamaño estándar de pantalla)
        # 54mm = 54 * 96 / 25.4 ≈ 204 píxeles
        # 85.6mm = 85.6 * 96 / 25.4 ≈ 323 píxeles
        self.tamano_real_px_ancho = int(54 * 96 / 25.4)  # ~204px
        self.tamano_real_px_alto = int(85.6 * 96 / 25.4)  # ~323px
        self.label_preview.setMinimumSize(self.tamano_real_px_ancho + 40, self.tamano_real_px_alto + 40)
        self.label_preview.setStyleSheet(
            "background-color: #ffffff; border: 2px solid #555; padding: 20px;"
        )
        self.label_preview.setText("La vista previa aparecerá aquí")
        
        container_layout.addWidget(self.label_preview)
        self.scroll.setWidget(self.container_widget)
        layout.addWidget(self.scroll)
    
    def _seleccionar_color_fondo(self):
        """Abre diálogo para seleccionar color de fondo de la vista previa"""
        color = QColorDialog.getColor(QColor(self.color_fondo_actual), self, "Seleccionar Color de Fondo")
        if color.isValid():
            self.color_fondo_actual = color.name()
            self.scroll.setStyleSheet(f"background-color: {self.color_fondo_actual};")
            self.boton_color_fondo.setStyleSheet(f"background-color: {self.color_fondo_actual}; color: {'white' if color.lightness() < 128 else 'black'}; padding: 5px;")
    
    def actualizar_preview(self, imagen_pil: Image.Image):
        """
        Actualiza la vista previa con una imagen PIL mostrándola a tamaño real
        
        Args:
            imagen_pil: Imagen PIL del carnet (debe estar a 300 DPI)
        """
        # Ocultar web_view si está visible (modo HTML)
        if self.usando_html and self.web_view:
            self.web_view.hide()
            self.usando_html = False
        
        # Mostrar label
        self.label_preview.show()
        
        if imagen_pil is None:
            self.label_preview.setText("No hay vista previa disponible")
            return
        
        self.imagen_actual = imagen_pil
        
        # Convertir PIL Image a QPixmap
        try:
            # Convertir a bytes
            img_bytes = io.BytesIO()
            imagen_pil.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Crear QImage desde bytes
            qimage = QImage.fromData(img_bytes.getvalue())
            
            if qimage.isNull():
                self.label_preview.setText("Error: No se pudo cargar la imagen")
                return
            
            # Obtener DPI real de la pantalla
            screen = QApplication.primaryScreen()
            if screen:
                dpi_fisico = screen.physicalDotsPerInch()
            else:
                dpi_fisico = 96  # DPI por defecto
            
            # La imagen está a 300 DPI, necesitamos escalarla al tamaño real en pantalla
            # Tamaño real de la tarjeta: 54mm x 85.6mm
            # Convertir mm a píxeles según el DPI de la pantalla
            # 1 pulgada = 25.4mm
            # píxeles = (mm * DPI) / 25.4
            
            ancho_real_px = int(54 * dpi_fisico / 25.4)
            alto_real_px = int(85.6 * dpi_fisico / 25.4)
            
            # Escalar la imagen al tamaño real en pantalla
            qimage_escalada = qimage.scaled(
                ancho_real_px,
                alto_real_px,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            pixmap = QPixmap.fromImage(qimage_escalada)
            
            if pixmap.isNull():
                self.label_preview.setText("Error: No se pudo crear el pixmap")
                return
            
            self.label_preview.setPixmap(pixmap)
            self.label_preview.setText("")
            self.label_preview.update()  # Forzar actualización
            
            # Ajustar el tamaño mínimo del label al tamaño de la imagen escalada
            self.label_preview.setMinimumSize(
                ancho_real_px + 40,
                alto_real_px + 40
            )
        except Exception as e:
            self.label_preview.setText(f"Error al mostrar vista previa: {str(e)}")
    
    def actualizar_preview_html(self, html_content: str, ancho: int, alto: int):
        """
        Actualiza la vista previa mostrando HTML directamente
        
        Args:
            html_content: Contenido HTML a mostrar
            ancho: Ancho del carnet en píxeles (a 300 DPI)
            alto: Alto del carnet en píxeles (a 300 DPI)
        """
        # Ocultar label si está visible
        if not self.usando_html:
            self.label_preview.hide()
            self.usando_html = True
        
        # Crear o reutilizar QWebEngineView
        if self.web_view is None:
            self.web_view = QWebEngineView()
            self.web_view.settings().setAttribute(
                self.web_view.settings().WebAttribute.LocalContentCanAccessRemoteUrls, True
            )
            self.web_view.settings().setAttribute(
                self.web_view.settings().WebAttribute.JavascriptEnabled, True
            )
            
            # Deshabilitar scrollbars
            self.web_view.page().settings().setAttribute(
                self.web_view.page().settings().WebAttribute.ShowScrollBars, False
            )
            
            # Obtener DPI real de la pantalla para escalar
            screen = QApplication.primaryScreen()
            if screen:
                dpi_fisico = screen.physicalDotsPerInch()
            else:
                dpi_fisico = 96
            
            # Calcular tamaño real en pantalla (54mm x 85.6mm)
            # La imagen está a 300 DPI, pero la pantalla tiene otro DPI
            # Necesitamos escalar proporcionalmente
            # Tamaño real físico: 54mm x 85.6mm
            ancho_real_px = int(54 * dpi_fisico / 25.4)
            alto_real_px = int(85.6 * dpi_fisico / 25.4)
            
            # Establecer tamaño fijo exacto
            self.web_view.setFixedSize(ancho_real_px, alto_real_px)
            self.web_view.setStyleSheet("background-color: transparent; border: none;")
            
            # Agregar al layout
            container_layout = self.container_widget.layout()
            container_layout.addWidget(self.web_view)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Asegurar que el tamaño esté correcto - usar tamaño exacto del carnet
        screen = QApplication.primaryScreen()
        if screen:
            dpi_fisico = screen.physicalDotsPerInch()
        else:
            dpi_fisico = 96
        
        # Calcular tamaño real en pantalla (54mm x 85.6mm)
        ancho_real_px = int(54 * dpi_fisico / 25.4)
        alto_real_px = int(85.6 * dpi_fisico / 25.4)
        
        # Establecer tamaño exacto del carnet
        self.web_view.setFixedSize(ancho_real_px, alto_real_px)
        
        # Calcular factor de escala para que el HTML (ancho x alto) quepa exactamente en el viewport
        # El HTML está a 300 DPI (637x1010), pero necesitamos escalarlo al tamaño real en pantalla
        factor_escala_ancho = ancho_real_px / ancho
        factor_escala_alto = alto_real_px / alto
        # Usar el menor para mantener proporción y que quepa completamente
        factor_escala = min(factor_escala_ancho, factor_escala_alto)
        
        # Modificar HTML para que se escale correctamente y no tenga scroll
        html_modificado = html_content
        if '<head>' in html_modificado and '</head>' in html_modificado:
            # Insertar estilos para eliminar scroll y escalar el contenido
            estilo_adicional = f"""
            <style>
                html {{
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                    width: 100%;
                    height: 100%;
                }}
                body {{
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                    width: {ancho}px;
                    height: {alto}px;
                    transform-origin: top left;
                    transform: scale({factor_escala});
                }}
            </style>
            """
            html_modificado = html_modificado.replace('</head>', estilo_adicional + '</head>')
        
        # Cargar HTML
        self.web_view.setHtml(html_modificado)
        self.web_view.show()
    
    def limpiar_preview(self):
        """Limpia la vista previa"""
        if self.web_view:
            self.web_view.hide()
            self.web_view = None
            self.usando_html = False
        
        self.label_preview.show()
        self.label_preview.clear()
        self.label_preview.setText("La vista previa aparecerá aquí")
        self.imagen_actual = None

