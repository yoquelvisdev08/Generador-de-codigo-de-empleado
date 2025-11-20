"""
Panel de generación de códigos de barras
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QGroupBox, QHBoxLayout,
                             QSpinBox, QCheckBox, QRadioButton, QButtonGroup, QApplication,
                             QScrollArea)
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
        
        # Crear QScrollArea para scroll vertical
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # Permite que el widget interno se redimensione
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Widget contenedor para el contenido scrolleable
        widget_contenido = QWidget()
        layout_contenido = QVBoxLayout()
        layout_contenido.setContentsMargins(0, 0, 0, 0)
        layout_contenido.setSpacing(5)
        widget_contenido.setLayout(layout_contenido)
        
        # Un solo QGroupBox que envuelve todo
        grupo_principal = QGroupBox("Generar Código de Barras")
        layout_grupo = QVBoxLayout()
        grupo_principal.setLayout(layout_grupo)
        
        label_formato = QLabel("Formato (opcional):")
        layout_grupo.addWidget(label_formato)
        
        self.combo_formato = QComboBox()
        self.combo_formato.addItems(self.formatos_disponibles)
        layout_grupo.addWidget(self.combo_formato)
        
        label_nombres = QLabel("Nombres del Empleado:")
        layout_grupo.addWidget(label_nombres)
        
        self.campo_nombres_empleado = QLineEdit()
        self.campo_nombres_empleado.setPlaceholderText("Ejemplo: Juan")
        layout_grupo.addWidget(self.campo_nombres_empleado)
        
        label_apellidos = QLabel("Apellidos del Empleado:")
        layout_grupo.addWidget(label_apellidos)
        
        self.campo_apellidos_empleado = QLineEdit()
        self.campo_apellidos_empleado.setPlaceholderText("Ejemplo: Pérez")
        layout_grupo.addWidget(self.campo_apellidos_empleado)
        
        # Separador visual (opcional, para mejor organización)
        separador1 = QLabel("─────────────────────────────────────")
        separador1.setStyleSheet("color: #ccc;")
        layout_grupo.addWidget(separador1)
        
        # Opciones directamente en el layout principal (sin sub-grupo)
        
        # Tipo de caracteres
        label_tipo = QLabel("Tipo de caracteres:")
        layout_grupo.addWidget(label_tipo)
        
        self.button_group_tipo = QButtonGroup(self)
        self.radio_alfanumerico = QRadioButton("Alfanumérico (0-9, A-Z)")
        self.radio_numerico = QRadioButton("Numérico (0-9)")
        self.radio_solo_letras = QRadioButton("Solo Letras (A-Z)")
        self.radio_alfanumerico.setChecked(True)
        
        self.button_group_tipo.addButton(self.radio_alfanumerico, 0)
        self.button_group_tipo.addButton(self.radio_numerico, 1)
        self.button_group_tipo.addButton(self.radio_solo_letras, 2)
        
        layout_grupo.addWidget(self.radio_alfanumerico)
        layout_grupo.addWidget(self.radio_numerico)
        layout_grupo.addWidget(self.radio_solo_letras)
        
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
        layout_grupo.addLayout(layout_cantidad)
        
        # Opción de incluir nombre (opcional)
        self.check_incluir_nombre = QCheckBox("Incluir nombre del empleado en el código (opcional)")
        self.check_incluir_nombre.setChecked(False)  # Opcional, no marcado por defecto
        self.check_incluir_nombre.setToolTip(
            "Si está marcado, el código incluirá las primeras letras del nombre del empleado"
        )
        layout_grupo.addWidget(self.check_incluir_nombre)
        
        # Opción de texto personalizado (opcional)
        self.check_texto_personalizado = QCheckBox("Crear texto personalizado para el código de barras (opcional)")
        self.check_texto_personalizado.setChecked(False)  # Opcional, no marcado por defecto
        self.check_texto_personalizado.setToolTip(
            "Si está marcado, podrá ingresar un texto personalizado que se incluirá en el código de barras"
        )
        layout_grupo.addWidget(self.check_texto_personalizado)
        
        # Contenedor para label e input de texto personalizado (oculto por defecto)
        self.contenedor_texto_personalizado = QWidget()
        layout_texto_personalizado = QVBoxLayout()
        layout_texto_personalizado.setContentsMargins(0, 5, 0, 5)  # Márgenes superior e inferior
        layout_texto_personalizado.setSpacing(5)  # Espacio entre label e input
        self.contenedor_texto_personalizado.setLayout(layout_texto_personalizado)
        self.contenedor_texto_personalizado.setVisible(False)  # Oculto por defecto
        
        label_texto_personalizado = QLabel("Texto personalizado:")
        layout_texto_personalizado.addWidget(label_texto_personalizado)
        
        self.campo_texto_personalizado = QLineEdit()
        self.campo_texto_personalizado.setPlaceholderText("Ingrese el texto personalizado para el código de barras")
        # Establecer tamaño mínimo para que se expanda correctamente
        self.campo_texto_personalizado.setMinimumHeight(35)
        # Aplicar estilo con padding y borde visible
        self.campo_texto_personalizado.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ccc;
                border-radius: 4px;
                font-size: 12pt;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
            }
        """)
        layout_texto_personalizado.addWidget(self.campo_texto_personalizado)
        
        layout_grupo.addWidget(self.contenedor_texto_personalizado)
        
        # Función para mostrar/ocultar el contenedor y actualizar el layout
        def mostrar_ocultar_texto_personalizado(checked: bool):
            self.contenedor_texto_personalizado.setVisible(checked)
            # Forzar actualización del layout cuando se muestra
            if checked:
                # Actualizar geometría de todos los contenedores
                self.contenedor_texto_personalizado.updateGeometry()
                self.contenedor_texto_personalizado.adjustSize()
                grupo_principal.updateGeometry()
                grupo_principal.adjustSize()
                self.updateGeometry()
                self.adjustSize()
                # Forzar recálculo del layout
                QApplication.processEvents()
                # Segunda actualización para asegurar que se expanda
                self.contenedor_texto_personalizado.updateGeometry()
                grupo_principal.updateGeometry()
                self.updateGeometry()
        
        # Conectar checkbox para mostrar/ocultar el contenedor completo
        self.check_texto_personalizado.toggled.connect(mostrar_ocultar_texto_personalizado)
        
        # Separador visual
        separador2 = QLabel("─────────────────────────────────────")
        separador2.setStyleSheet("color: #ccc;")
        layout_grupo.addWidget(separador2)
        
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
        
        # Separador visual antes de la vista previa
        separador3 = QLabel("─────────────────────────────────────")
        separador3.setStyleSheet("color: #ccc;")
        layout_grupo.addWidget(separador3)
        
        # Vista Previa dentro del mismo grupo
        label_vista_previa_titulo = QLabel("Vista Previa:")
        label_vista_previa_titulo.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout_grupo.addWidget(label_vista_previa_titulo)
        
        self.label_vista_previa = QLabel()
        self.label_vista_previa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_vista_previa.setMinimumHeight(200)
        self.label_vista_previa.setStyleSheet(
            "border: 1px solid #ccc; background-color: white;"
        )
        self.label_vista_previa.setText("La vista previa aparecerá aquí")
        layout_grupo.addWidget(self.label_vista_previa)
        
        # Agregar el grupo principal al layout de contenido
        layout_contenido.addWidget(grupo_principal)
        layout_contenido.addStretch()
        
        # Configurar el scroll area con el widget de contenido
        scroll_area.setWidget(widget_contenido)
        
        # Agregar el scroll area al layout principal
        layout.addWidget(scroll_area)
    
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
            'nombres': self.campo_nombres_empleado.text().strip(),
            'apellidos': self.campo_apellidos_empleado.text().strip(),
            'formato': self.combo_formato.currentText(),
            'descripcion': self.campo_descripcion.text().strip(),  # Código de empleado (obligatorio)
            'tipo_caracteres': tipo_caracteres,
            'cantidad_caracteres': self.spin_cantidad.value(),
            'incluir_nombre': self.check_incluir_nombre.isChecked(),
            'texto_personalizado': self.campo_texto_personalizado.text().strip() if self.check_texto_personalizado.isChecked() else None
        }
    
    def obtener_opciones_id(self) -> dict:
        """
        Obtiene las opciones de personalización del ID
        
        Returns:
            Diccionario con las opciones
        """
        datos = self.obtener_datos()
        # Crear nombre completo para generación de ID
        nombre_completo = f"{datos['nombres']} {datos['apellidos']}".strip()
        return {
            'tipo_caracteres': datos['tipo_caracteres'],
            'cantidad_caracteres': datos['cantidad_caracteres'],
            'incluir_nombre': datos['incluir_nombre'],
            'nombre_empleado': nombre_completo,  # Mantener este nombre por compatibilidad con el generador de ID
            'texto_personalizado': datos['texto_personalizado']
        }
    
    def limpiar_formulario(self):
        """Limpia los campos del formulario"""
        self.campo_nombres_empleado.clear()
        self.campo_apellidos_empleado.clear()
        self.campo_descripcion.clear()
        # Restaurar estilo del campo de código de empleado
        self.campo_descripcion.setStyleSheet("border: 2px solid #dc3545;")
        # Limpiar texto personalizado
        self.check_texto_personalizado.setChecked(False)
        self.campo_texto_personalizado.clear()
    
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
        self.campo_nombres_empleado.textChanged.connect(callback)
        self.campo_apellidos_empleado.textChanged.connect(callback)
        self.radio_alfanumerico.toggled.connect(callback)
        self.radio_numerico.toggled.connect(callback)
        self.radio_solo_letras.toggled.connect(callback)
        self.spin_cantidad.valueChanged.connect(callback)
        self.check_incluir_nombre.toggled.connect(callback)
        self.check_texto_personalizado.toggled.connect(callback)
        self.campo_texto_personalizado.textChanged.connect(callback)
    
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

