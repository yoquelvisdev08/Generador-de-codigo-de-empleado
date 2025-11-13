"""
Ventana principal de la aplicación
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QSplitter, QLabel, 
                             QStackedWidget, QHBoxLayout, QPushButton, QFrame, QMenu)
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
        layout_principal.setContentsMargins(0, 0, 0, 0)  # Sin márgenes para que el navbar llegue a los bordes
        layout_principal.setSpacing(0)
        widget_principal.setLayout(layout_principal)
        
        # Navbar permanente
        self._crear_navbar()
        layout_principal.addWidget(self.navbar)
        
        # Contenedor principal con márgenes
        contenedor_principal = QWidget()
        layout_contenedor = QVBoxLayout()
        layout_contenedor.setContentsMargins(5, 5, 5, 5)
        layout_contenedor.setSpacing(5)
        contenedor_principal.setLayout(layout_contenedor)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)  # Evitar que se colapsen los paneles
        
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
        
        layout_contenedor.addWidget(self.splitter)
        layout_principal.addWidget(contenedor_principal)
        
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
    
    def _crear_navbar(self):
        """Crea el navbar permanente en la parte superior con menú desplegable"""
        self.navbar = QFrame()
        self.navbar.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        self.navbar.setFixedHeight(32)  # Menos ancho (altura reducida)
        
        layout_navbar = QHBoxLayout()
        layout_navbar.setContentsMargins(15, 4, 15, 4)  # Márgenes verticales reducidos
        layout_navbar.setSpacing(0)
        self.navbar.setLayout(layout_navbar)
        
        # Botón "Tools" con menú desplegable - diseño minimalista
        self.boton_tools = QPushButton("Tools")
        self.boton_tools.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333333;
                font-size: 11pt;
                padding: 4px 8px;
                border: none;
                text-align: left;
            }
            QPushButton::menu-indicator {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 12px;
                height: 12px;
                padding-right: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #eeeeee;
            }
        """)
        self.boton_tools.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Crear menú desplegable - diseño minimalista
        menu_tools = QMenu(self.boton_tools)
        menu_tools.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px 8px 16px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #f5f5f5;
                color: #000000;
            }
        """)
        
        # Acción "Código de Barras"
        accion_codigo_barras = menu_tools.addAction("Código de Barras")
        
        # Acción "Crear Carnet"
        accion_crear_carnet = menu_tools.addAction("Crear Carnet")
        
        # Guardar referencias para conectar en el controlador
        self.accion_codigo_barras = accion_codigo_barras
        self.accion_crear_carnet = accion_crear_carnet
        
        # Asignar menú al botón
        self.boton_tools.setMenu(menu_tools)
        
        layout_navbar.addWidget(self.boton_tools)
        layout_navbar.addStretch()  # Empujar hacia la izquierda
        
        # Indicador de vista actual (se actualizará dinámicamente)
        self.vista_actual = "codigo_barras"
        self._actualizar_estilo_navbar()
    
    def _actualizar_estilo_navbar(self):
        """Actualiza el estilo del menú según la vista actual"""
        # El estilo del botón Tools se mantiene constante
        # Las acciones del menú se pueden actualizar si es necesario
        pass
    
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
        # Actualizar navbar
        self.vista_actual = "codigo_barras"
        self._actualizar_estilo_navbar()
    
    def mostrar_vista_carnet(self):
        """Muestra la vista de creación de carnet"""
        self.stacked_widget.setCurrentIndex(1)
        # Ocultar el panel de listado para pantalla completa
        self.list_panel.hide()
        # Actualizar navbar
        self.vista_actual = "carnet"
        self._actualizar_estilo_navbar()

