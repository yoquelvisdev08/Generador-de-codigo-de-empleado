"""
Panel de generación de códigos de barras
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QGroupBox, QHBoxLayout,
                             QSpinBox, QCheckBox, QRadioButton, QButtonGroup)
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
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
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
        
        # Grupo de opciones de personalización del ID
        grupo_opciones = QGroupBox("Opciones de Código de Barras")
        layout_opciones = QVBoxLayout()
        grupo_opciones.setLayout(layout_opciones)
        
        # Tipo de caracteres
        label_tipo = QLabel("Tipo de caracteres:")
        layout_opciones.addWidget(label_tipo)
        
        self.button_group_tipo = QButtonGroup(self)
        self.radio_alfanumerico = QRadioButton("Alfanumérico (0-9, A-Z)")
        self.radio_numerico = QRadioButton("Numérico (0-9)")
        self.radio_solo_letras = QRadioButton("Solo Letras (A-Z)")
        self.radio_alfanumerico.setChecked(True)
        
        self.button_group_tipo.addButton(self.radio_alfanumerico, 0)
        self.button_group_tipo.addButton(self.radio_numerico, 1)
        self.button_group_tipo.addButton(self.radio_solo_letras, 2)
        
        layout_opciones.addWidget(self.radio_alfanumerico)
        layout_opciones.addWidget(self.radio_numerico)
        layout_opciones.addWidget(self.radio_solo_letras)
        
        # Cantidad de caracteres
        layout_cantidad = QHBoxLayout()
        label_cantidad = QLabel("Cantidad de caracteres:")
        layout_cantidad.addWidget(label_cantidad)
        
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(3)
        self.spin_cantidad.setMaximum(20)
        self.spin_cantidad.setValue(10)
        layout_cantidad.addWidget(self.spin_cantidad)
        layout_cantidad.addStretch()
        layout_opciones.addLayout(layout_cantidad)
        
        # Opción de incluir nombre (opcional)
        self.check_incluir_nombre = QCheckBox("Incluir nombre del empleado en el código (opcional)")
        self.check_incluir_nombre.setChecked(False)  # Opcional, no marcado por defecto
        self.check_incluir_nombre.setToolTip(
            "Si está marcado, el código incluirá las primeras letras del nombre del empleado"
        )
        layout_opciones.addWidget(self.check_incluir_nombre)
        
        layout_grupo.addWidget(grupo_opciones)
        
        self.label_id_generado = QLabel()
        self.label_id_generado.setStyleSheet(
            "color: #0066cc; font-size: 10pt; font-weight: bold; "
            "padding: 5px; background-color: #f0f0f0; border: 1px solid #ccc;"
        )
        layout_grupo.addWidget(self.label_id_generado)
        
        label_codigo_empleado = QLabel("Código de Empleado: *")
        label_codigo_empleado.setStyleSheet("font-weight: bold; color: #dc3545;")
        layout_grupo.addWidget(label_codigo_empleado)
        
        self.campo_descripcion = QLineEdit()
        self.campo_descripcion.setPlaceholderText("Ingrese el código de empleado (obligatorio)")
        self.campo_descripcion.setStyleSheet("border: 2px solid #dc3545;")  # Borde rojo para indicar obligatorio
        # Conectar señal para cambiar estilo cuando se ingrese texto
        self.campo_descripcion.textChanged.connect(self._validar_campo_codigo_empleado)
        layout_grupo.addWidget(self.campo_descripcion)
        
        self.boton_generar = QPushButton("Generar Código de Barras")
        self.boton_generar.setMinimumHeight(40)
        layout_grupo.addWidget(self.boton_generar)
        
        self.boton_crear_carnet = QPushButton("Crear Carnet")
        self.boton_crear_carnet.setMinimumHeight(40)
        self.boton_crear_carnet.setStyleSheet("background-color: #6f42c1; color: white; font-weight: bold;")
        self.boton_crear_carnet.setToolTip("Abre la ventana para crear un carnet")
        layout_grupo.addWidget(self.boton_crear_carnet)
        
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
        # Determinar tipo de caracteres seleccionado
        if self.radio_alfanumerico.isChecked():
            tipo_caracteres = "alfanumerico"
        elif self.radio_numerico.isChecked():
            tipo_caracteres = "numerico"
        else:
            tipo_caracteres = "solo_letras"
        
        return {
            'nombre_empleado': self.campo_nombre_empleado.text().strip(),
            'formato': self.combo_formato.currentText(),
            'descripcion': self.campo_descripcion.text().strip(),  # Código de empleado (obligatorio)
            'tipo_caracteres': tipo_caracteres,
            'cantidad_caracteres': self.spin_cantidad.value(),
            'incluir_nombre': self.check_incluir_nombre.isChecked()
        }
    
    def obtener_opciones_id(self) -> dict:
        """
        Obtiene las opciones de personalización del ID
        
        Returns:
            Diccionario con las opciones
        """
        datos = self.obtener_datos()
        return {
            'tipo_caracteres': datos['tipo_caracteres'],
            'cantidad_caracteres': datos['cantidad_caracteres'],
            'incluir_nombre': datos['incluir_nombre'],
            'nombre_empleado': datos['nombre_empleado']
        }
    
    def limpiar_formulario(self):
        """Limpia los campos del formulario"""
        self.campo_nombre_empleado.clear()
        self.campo_descripcion.clear()
        # Restaurar estilo del campo de código de empleado
        self.campo_descripcion.setStyleSheet("border: 2px solid #dc3545;")
    
    def actualizar_id_preview(self, siguiente_id: str):
        """
        Actualiza la vista previa del ID que se generará
        
        Args:
            siguiente_id: ID que se generará
        """
        self.label_id_generado.setText(f"ID que se generará: {siguiente_id}")
    
    def _validar_campo_codigo_empleado(self):
        """Valida y actualiza el estilo del campo de código de empleado"""
        texto = self.campo_descripcion.text().strip()
        if texto:
            # Si tiene texto, cambiar a borde verde
            self.campo_descripcion.setStyleSheet("border: 2px solid #28a745;")
        else:
            # Si está vacío, mantener borde rojo
            self.campo_descripcion.setStyleSheet("border: 2px solid #dc3545;")
    
    def conectar_senales_actualizacion(self, callback):
        """
        Conecta las señales de los controles para actualizar el ID en tiempo real
        
        Args:
            callback: Función a llamar cuando cambien las opciones
        """
        self.campo_nombre_empleado.textChanged.connect(callback)
        self.radio_alfanumerico.toggled.connect(callback)
        self.radio_numerico.toggled.connect(callback)
        self.radio_solo_letras.toggled.connect(callback)
        self.spin_cantidad.valueChanged.connect(callback)
        self.check_incluir_nombre.toggled.connect(callback)
    
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

