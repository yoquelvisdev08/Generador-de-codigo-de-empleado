"""
Panel para creación de carnet
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSplitter
from PyQt6.QtCore import Qt

from src.views.widgets.carnet_preview_panel import CarnetPreviewPanel
from src.views.widgets.carnet_controls_panel import CarnetControlsPanel
from src.views.widgets.carnet_employees_panel import CarnetEmployeesPanel


class CarnetPanel(QWidget):
    """Panel para crear carnet"""
    
    def __init__(self, parent=None):
        """
        Inicializa el panel de carnet
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(5, 5, 5, 5)
        layout_principal.setSpacing(5)
        self.setLayout(layout_principal)
        
        # Botón para volver a la vista de generación
        self.boton_volver = QPushButton("← Volver a Generar Código")
        self.boton_volver.setStyleSheet("background-color: #6c757d; color: white; font-weight: bold; padding: 10px;")
        self.boton_volver.setMinimumHeight(40)
        self.boton_volver.setMaximumHeight(40)
        layout_principal.addWidget(self.boton_volver)
        
        # Splitter horizontal para los dos paneles superiores (12% vista previa, 88% controles - aumentado 20%)
        splitter_superior = QSplitter(Qt.Orientation.Horizontal)
        splitter_superior.setChildrenCollapsible(False)
        
        # Panel izquierdo: Vista previa (12% - aumentado 20% desde 10%)
        self.preview_panel = CarnetPreviewPanel()
        self.preview_panel.setMinimumWidth(180)  # Ancho mínimo aumentado
        splitter_superior.addWidget(self.preview_panel)
        
        # Panel derecho: Controles de diseño (88%)
        self.controls_panel = CarnetControlsPanel()
        self.controls_panel.setMinimumWidth(300)  # Ancho mínimo
        splitter_superior.addWidget(self.controls_panel)
        
        # Tamaños proporcionales (12% vista previa, 88% controles - aumentado 20%)
        splitter_superior.setSizes([12, 88])  # 12% y 88% respectivamente
        
        # Panel inferior: Lista de empleados y acciones (100% de ancho)
        self.employees_panel = CarnetEmployeesPanel()
        self.employees_panel.setMinimumHeight(150)  # Altura mínima reducida
        
        # Splitter vertical principal para dividir superior e inferior
        splitter_principal = QSplitter(Qt.Orientation.Vertical)
        splitter_principal.setChildrenCollapsible(False)
        splitter_principal.addWidget(splitter_superior)  # Paneles superiores
        splitter_principal.addWidget(self.employees_panel)  # Panel inferior
        
        # Proporciones: 60% superior (aumentado 20%), 40% inferior (reducido)
        splitter_principal.setSizes([60, 40])  # 60% superior y 40% inferior
        
        layout_principal.addWidget(splitter_principal)

