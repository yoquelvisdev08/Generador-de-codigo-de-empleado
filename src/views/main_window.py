"""
Ventana principal de la aplicación
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter, QLabel
from PyQt6.QtCore import Qt

from config.settings import APP_NAME, APP_AUTHOR, WINDOW_WIDTH, WINDOW_HEIGHT
from src.views.widgets.generation_panel import GenerationPanel
from src.views.widgets.list_panel import ListPanel


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
        self.list_panel = None
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle(f"{APP_NAME} - {APP_AUTHOR}")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        widget_principal = QWidget()
        self.setCentralWidget(widget_principal)
        
        layout_principal = QVBoxLayout()
        widget_principal.setLayout(layout_principal)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout_principal.addWidget(splitter)
        
        self.generation_panel = GenerationPanel(self.formatos_disponibles)
        self.list_panel = ListPanel()
        
        splitter.addWidget(self.generation_panel)
        splitter.addWidget(self.list_panel)
        splitter.setSizes([400, 800])
        
        self.crear_barra_estado()
    
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

