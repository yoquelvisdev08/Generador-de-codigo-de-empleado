"""
Panel de generación de códigos de barras
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QGroupBox)
from PyQt6.QtCore import Qt


class GenerationPanel(QWidget):
    """Panel para generar nuevos códigos de barras"""
    
    def __init__(self, formatos_disponibles: list, parent=None):
        """
        Inicializa el panel de generación
        
        Args:
            formatos_disponibles: Lista de formatos disponibles
            parent: Widget padre
        """
        super().__init__(parent)
        self.formatos_disponibles = formatos_disponibles
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        grupo_generacion = QGroupBox("Generar Nuevo Código de Barras")
        layout_grupo = QVBoxLayout()
        grupo_generacion.setLayout(layout_grupo)
        
        label_formato = QLabel("Formato:")
        layout_grupo.addWidget(label_formato)
        
        self.combo_formato = QComboBox()
        self.combo_formato.addItems(self.formatos_disponibles)
        layout_grupo.addWidget(self.combo_formato)
        
        label_nombre = QLabel("Nombre del Empleado:")
        layout_grupo.addWidget(label_nombre)
        
        self.campo_nombre_empleado = QLineEdit()
        self.campo_nombre_empleado.setPlaceholderText("Ejemplo: Juan Pérez")
        layout_grupo.addWidget(self.campo_nombre_empleado)
        
        self.label_id_generado = QLabel()
        self.label_id_generado.setStyleSheet(
            "color: #0066cc; font-size: 10pt; font-weight: bold; "
            "padding: 5px; background-color: #f0f0f0; border: 1px solid #ccc;"
        )
        layout_grupo.addWidget(self.label_id_generado)
        
        label_descripcion = QLabel("Descripción (opcional):")
        layout_grupo.addWidget(label_descripcion)
        
        self.campo_descripcion = QLineEdit()
        self.campo_descripcion.setPlaceholderText("Descripción del código")
        layout_grupo.addWidget(self.campo_descripcion)
        
        self.boton_generar = QPushButton("Generar Código de Barras")
        self.boton_generar.setMinimumHeight(40)
        layout_grupo.addWidget(self.boton_generar)
        
        layout.addWidget(grupo_generacion)
        
        grupo_vista_previa = QGroupBox("Vista Previa")
        layout_vista = QVBoxLayout()
        grupo_vista_previa.setLayout(layout_vista)
        
        self.label_vista_previa = QLabel()
        self.label_vista_previa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_vista_previa.setMinimumHeight(200)
        self.label_vista_previa.setStyleSheet(
            "border: 1px solid #ccc; background-color: white;"
        )
        self.label_vista_previa.setText("La vista previa aparecerá aquí")
        layout_vista.addWidget(self.label_vista_previa)
        
        layout.addWidget(grupo_vista_previa)
        layout.addStretch()
    
    def obtener_datos(self) -> dict:
        """
        Obtiene los datos del formulario
        
        Returns:
            Diccionario con los datos del formulario
        """
        return {
            'nombre_empleado': self.campo_nombre_empleado.text().strip(),
            'formato': self.combo_formato.currentText(),
            'descripcion': self.campo_descripcion.text().strip() or None
        }
    
    def limpiar_formulario(self):
        """Limpia los campos del formulario"""
        self.campo_nombre_empleado.clear()
        self.campo_descripcion.clear()
    
    def actualizar_id_preview(self, siguiente_id: str):
        """
        Actualiza la vista previa del ID que se generará
        
        Args:
            siguiente_id: ID que se generará
        """
        self.label_id_generado.setText(f"ID que se generará: {siguiente_id}")
    
    def mostrar_vista_previa(self, ruta_imagen: str):
        """
        Muestra la vista previa de la imagen
        
        Args:
            ruta_imagen: Ruta a la imagen
        """
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtCore import Qt as QtCore
        
        pixmap = QPixmap(ruta_imagen)
        if not pixmap.isNull():
            pixmap_escalado = pixmap.scaled(
                350, 150,
                QtCore.AspectRatioMode.KeepAspectRatio,
                QtCore.TransformationMode.SmoothTransformation
            )
            self.label_vista_previa.setPixmap(pixmap_escalado)

