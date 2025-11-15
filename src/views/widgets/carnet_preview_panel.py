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
        self.zoom_actual = 1.0  # Nivel de zoom actual (1.0 = 100%)
        self.tamano_base_ancho = None  # Tamaño base del carnet (sin zoom)
        self.tamano_base_alto = None
        self.html_content_actual = None  # HTML actual para recargar con zoom
        self.html_ancho = None  # Ancho del HTML (a 300 DPI)
        self.html_alto = None  # Alto del HTML (a 300 DPI)
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
        
        # Controles de fondo de vista previa y zoom
        layout_controles_fondo = QHBoxLayout()
        label_fondo = QLabel("Fondo:")
        label_fondo.setStyleSheet("font-size: 9pt;")
        self.color_fondo_actual = "#2b2b31"  # Color por defecto
        self.boton_color_fondo = QPushButton("Color")
        self.boton_color_fondo.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color_fondo_actual};
                color: white;
                font-size: 9pt;
                padding: 3px 8px;
                border: none;
                border-radius: 3px;
                min-width: 50px;
                min-height: 22px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """)
        self.boton_color_fondo.clicked.connect(self._seleccionar_color_fondo)
        layout_controles_fondo.addWidget(label_fondo)
        layout_controles_fondo.addWidget(self.boton_color_fondo)
        
        # Botones de zoom
        layout_controles_fondo.addSpacing(8)
        label_zoom = QLabel("Zoom:")
        label_zoom.setStyleSheet("font-size: 9pt;")
        layout_controles_fondo.addWidget(label_zoom)
        
        self.boton_zoom_menor = QPushButton("−")
        self.boton_zoom_menor.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-weight: bold;
                font-size: 10pt;
                padding: 2px 6px;
                border: none;
                border-radius: 3px;
                min-width: 22px;
                min-height: 22px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #484f54;
            }
        """)
        self.boton_zoom_menor.clicked.connect(self._zoom_menor)
        self.boton_zoom_menor.setToolTip("Disminuir zoom")
        layout_controles_fondo.addWidget(self.boton_zoom_menor)
        
        self.label_zoom_porcentaje = QLabel("100%")
        self.label_zoom_porcentaje.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 9pt;
                padding: 2px 6px;
                min-width: 40px;
                text-align: center;
            }
        """)
        layout_controles_fondo.addWidget(self.label_zoom_porcentaje)
        
        self.boton_zoom_mayor = QPushButton("+")
        self.boton_zoom_mayor.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-weight: bold;
                font-size: 10pt;
                padding: 2px 6px;
                border: none;
                border-radius: 3px;
                min-width: 22px;
                min-height: 22px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #484f54;
            }
        """)
        self.boton_zoom_mayor.clicked.connect(self._zoom_mayor)
        self.boton_zoom_mayor.setToolTip("Aumentar zoom")
        layout_controles_fondo.addWidget(self.boton_zoom_mayor)
        
        layout_controles_fondo.addStretch()
        layout.addLayout(layout_controles_fondo)
        
        # Área de scroll para la vista previa (sin scrollbars cuando se usa HTML)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setStyleSheet(f"background-color: {self.color_fondo_actual};")
        # Habilitar scrollbars cuando sea necesario (cuando hay zoom)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
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
    
    def _zoom_menor(self):
        """Disminuye el zoom de la vista previa"""
        if self.zoom_actual > 0.25:  # Mínimo 25%
            self.zoom_actual = max(0.25, self.zoom_actual - 0.25)
            self._aplicar_zoom()
    
    def _zoom_mayor(self):
        """Aumenta el zoom de la vista previa"""
        if self.zoom_actual < 4.0:  # Máximo 400%
            self.zoom_actual = min(4.0, self.zoom_actual + 0.25)
            self._aplicar_zoom()
    
    def _aplicar_zoom(self):
        """Aplica el zoom actual a la vista previa"""
        # Actualizar label de porcentaje
        porcentaje = int(self.zoom_actual * 100)
        self.label_zoom_porcentaje.setText(f"{porcentaje}%")
        
        # Habilitar/deshabilitar scrollbars según el zoom
        if self.zoom_actual > 1.0:
            self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Aplicar zoom según el tipo de vista previa
        if self.usando_html and self.web_view:
            self._aplicar_zoom_html()
        elif self.imagen_actual is not None:
            self._aplicar_zoom_imagen()
    
    def _aplicar_zoom_html(self):
        """Aplica zoom a la vista previa HTML"""
        if self.web_view is None:
            return
        
        # Si tenemos HTML guardado, recargarlo con el nuevo zoom
        if self.html_content_actual is not None and self.html_ancho is not None and self.html_alto is not None:
            self.actualizar_preview_html(self.html_content_actual, self.html_ancho, self.html_alto)
            return
        
        # Si no hay HTML guardado, solo ajustar el tamaño y zoom del web_view existente
        if self.tamano_base_ancho is None or self.tamano_base_alto is None:
            return
        
        # Obtener DPI real de la pantalla
        screen = QApplication.primaryScreen()
        if screen:
            dpi_fisico = screen.physicalDotsPerInch()
        else:
            dpi_fisico = 96
        
        # Calcular tamaño base (tamaño real en pantalla)
        ancho_base = int(54 * dpi_fisico / 25.4)
        alto_base = int(85.6 * dpi_fisico / 25.4)
        
        # Aplicar zoom
        ancho_zoom = int(ancho_base * self.zoom_actual)
        alto_zoom = int(alto_base * self.zoom_actual)
        
        # Establecer nuevo tamaño
        self.web_view.setFixedSize(ancho_zoom, alto_zoom)
        
        # Actualizar el zoom del web_view también para mejor calidad
        self.web_view.setZoomFactor(self.zoom_actual)
    
    def _aplicar_zoom_imagen(self):
        """Aplica zoom a la vista previa de imagen PIL"""
        if self.imagen_actual is None:
            return
        
        # Obtener DPI real de la pantalla
        screen = QApplication.primaryScreen()
        if screen:
            dpi_fisico = screen.physicalDotsPerInch()
        else:
            dpi_fisico = 96
        
        # Calcular tamaño base (tamaño real en pantalla)
        ancho_base = int(54 * dpi_fisico / 25.4)
        alto_base = int(85.6 * dpi_fisico / 25.4)
        
        # Aplicar zoom
        ancho_zoom = int(ancho_base * self.zoom_actual)
        alto_zoom = int(alto_base * self.zoom_actual)
        
        # Convertir PIL Image a QPixmap y escalar
        try:
            img_bytes = io.BytesIO()
            self.imagen_actual.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            qimage = QImage.fromData(img_bytes.getvalue())
            if qimage.isNull():
                return
            
            # Escalar la imagen con el zoom aplicado
            qimage_escalada = qimage.scaled(
                ancho_zoom,
                alto_zoom,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            pixmap = QPixmap.fromImage(qimage_escalada)
            if not pixmap.isNull():
                self.label_preview.setPixmap(pixmap)
                self.label_preview.setMinimumSize(ancho_zoom + 40, alto_zoom + 40)
        except Exception as e:
            print(f"Error al aplicar zoom a imagen: {e}")
    
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
        
        # Guardar tamaño base para el zoom
        screen = QApplication.primaryScreen()
        if screen:
            dpi_fisico = screen.physicalDotsPerInch()
        else:
            dpi_fisico = 96
        
        self.tamano_base_ancho = int(54 * dpi_fisico / 25.4)
        self.tamano_base_alto = int(85.6 * dpi_fisico / 25.4)
        
        # Aplicar zoom actual
        self._aplicar_zoom_imagen()
    
    def actualizar_preview_html(self, html_content: str, ancho: int, alto: int):
        """
        Actualiza la vista previa mostrando HTML directamente
        
        Args:
            html_content: Contenido HTML a mostrar
            ancho: Ancho del carnet en píxeles (a 300 DPI)
            alto: Alto del carnet en píxeles (a 300 DPI)
        """
        # Guardar HTML actual para poder recargarlo cuando cambie el zoom
        self.html_content_actual = html_content
        self.html_ancho = ancho
        self.html_alto = alto
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
        
        # Guardar tamaño base para el zoom
        self.tamano_base_ancho = ancho_real_px
        self.tamano_base_alto = alto_real_px
        
        # Calcular factor de escala base para que el HTML (ancho x alto) quepa exactamente en el viewport
        # El HTML está a 300 DPI (637x1010), pero necesitamos escalarlo al tamaño real en pantalla
        factor_escala_ancho = ancho_real_px / ancho
        factor_escala_alto = alto_real_px / alto
        # Usar el menor para mantener proporción y que quepa completamente
        factor_escala_base = min(factor_escala_ancho, factor_escala_alto)
        
        # Aplicar zoom del usuario: el widget se escala proporcionalmente
        ancho_con_zoom = int(ancho_real_px * self.zoom_actual)
        alto_con_zoom = int(alto_real_px * self.zoom_actual)
        
        # Establecer tamaño del carnet con zoom aplicado
        self.web_view.setFixedSize(ancho_con_zoom, alto_con_zoom)
        
        # Modificar HTML para que se escale correctamente al tamaño base
        # El zoom del usuario se aplicará usando setZoomFactor sobre el contenido ya escalado
        html_modificado = html_content
        if '<head>' in html_modificado and '</head>' in html_modificado:
            # Insertar estilos para escalar el contenido al tamaño base
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
                    transform: scale({factor_escala_base});
                }}
            </style>
            """
            html_modificado = html_modificado.replace('</head>', estilo_adicional + '</head>')
        
        # Establecer zoom del web_view para aplicar el zoom del usuario
        # Esto renderiza nativamente a alta resolución sin pixelación
        # El zoom se aplica sobre el contenido ya escalado al tamaño base
        self.web_view.setZoomFactor(self.zoom_actual)
        
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
        self.html_content_actual = None
        self.html_ancho = None
        self.html_alto = None
        self.zoom_actual = 1.0  # Resetear zoom a 100%
        self.label_zoom_porcentaje.setText("100%")

