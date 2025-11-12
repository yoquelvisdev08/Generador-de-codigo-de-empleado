"""
Ventana principal de la aplicación
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter, QLabel, QStackedWidget
from PyQt6.QtCore import Qt

from config.settings import APP_NAME, APP_AUTHOR, WINDOW_WIDTH, WINDOW_HEIGHT
from src.views.widgets.generation_panel import GenerationPanel
from src.views.widgets.list_panel import ListPanel
from src.views.carnet_window import CarnetPanel


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self, formatos_disponibles: list = None, parent=None):
        """
        Inicializa la ventana principal
        
        Args:
            formatos_disponibles: Lista de formatos disponibles para el panel de generación
            parent: Widget padre
        """
        super().__init__(parent)
        self.formatos_disponibles = formatos_disponibles or []
        self.generation_panel = None
        self.carnet_panel = None
        self.list_panel = None
        self.stacked_widget = None
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle(f"{APP_NAME} - {APP_AUTHOR}")
        
        # Tamaños responsivos: mínimo para laptops pequeñas, máximo flexible
        self.setMinimumSize(800, 600)  # Mínimo para laptops pequeñas
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        widget_principal = QWidget()
        self.setCentralWidget(widget_principal)
        
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(5, 5, 5, 5)
        layout_principal.setSpacing(5)
        widget_principal.setLayout(layout_principal)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)  # Evitar que se colapsen los paneles
        layout_principal.addWidget(self.splitter)
        
        # Crear QStackedWidget para cambiar entre vistas
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setMinimumWidth(300)  # Ancho mínimo para panel izquierdo
        
        # Panel de generación (vista principal)
        self.generation_panel = GenerationPanel(self.formatos_disponibles)
        self.stacked_widget.addWidget(self.generation_panel)
        
        # Panel de carnet (vista secundaria)
        self.carnet_panel = CarnetPanel()
        self.stacked_widget.addWidget(self.carnet_panel)
        
        # Panel de listado (se oculta en vista de carnet)
        self.list_panel = ListPanel()
        self.list_panel.setMinimumWidth(400)  # Ancho mínimo para panel de listado
        
        self.splitter.addWidget(self.stacked_widget)
        self.splitter.addWidget(self.list_panel)
        
        # Tamaños proporcionales (40% izquierda, 60% derecha)
        # Se ajustarán automáticamente al tamaño de la ventana
        ancho_total = self.width()
        self.splitter.setSizes([int(ancho_total * 0.4), int(ancho_total * 0.6)])
        
        self.crear_barra_estado()
        
        # No centrar automáticamente - se centrará cuando se muestre
        # self._centrar_ventana()
    
    def _centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            return
        screen = app.primaryScreen().geometry()
        size = self.frameGeometry()
        x = max(0, (screen.width() - size.width()) // 2)
        y = max(0, (screen.height() - size.height()) // 2)
        self.move(x, y)
    
    def crear_barra_estado(self):
        """Crea la barra de estado"""
        self.statusBar().showMessage("Listo")
        self.statusBar().addPermanentWidget(QLabel(APP_AUTHOR))
    
    def actualizar_estadisticas(self, mensaje: str):
        """
        Actualiza el mensaje de estadísticas en la barra de estado
        
        Args:
            mensaje: Mensaje a mostrar
        """
        self.statusBar().showMessage(mensaje)
    
    def mostrar_vista_generacion(self):
        """Muestra la vista de generación de códigos"""
        self.stacked_widget.setCurrentIndex(0)
        # Mostrar el panel de listado
        self.list_panel.show()
        # Restaurar tamaños proporcionales del splitter
        ancho_total = self.width()
        self.splitter.setSizes([int(ancho_total * 0.4), int(ancho_total * 0.6)])
    
    def mostrar_vista_carnet(self):
        """Muestra la vista de creación de carnet"""
        self.stacked_widget.setCurrentIndex(1)
        # Ocultar el panel de listado para pantalla completa
        self.list_panel.hide()

