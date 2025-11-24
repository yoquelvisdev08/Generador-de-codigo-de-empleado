"""
Panel de generación de códigos de barras de servicio
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QGroupBox, QHBoxLayout, QScrollArea,
                             QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
                             QSpinBox)
from PyQt6.QtCore import Qt


class ServicePanel(QWidget):
    """Panel para generar códigos de barras de servicio"""
    
    def __init__(self, parent=None):
        """
        Inicializa el panel de servicios
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.setLayout(layout)
        
        # Splitter horizontal para dividir formulario y tabla
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # Panel izquierdo: Formulario de generación
        widget_formulario = QWidget()
        layout_formulario = QVBoxLayout()
        layout_formulario.setContentsMargins(0, 0, 0, 0)
        layout_formulario.setSpacing(5)
        widget_formulario.setLayout(layout_formulario)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        widget_contenido = QWidget()
        layout_contenido = QVBoxLayout()
        layout_contenido.setContentsMargins(0, 0, 0, 0)
        layout_contenido.setSpacing(5)
        widget_contenido.setLayout(layout_contenido)
        
        grupo_principal = QGroupBox("Generar Código de Barras de Servicio")
        layout_grupo = QVBoxLayout()
        grupo_principal.setLayout(layout_grupo)
        
        label_nombre_servicio = QLabel("Nombre del Servicio: *")
        label_nombre_servicio.setStyleSheet("font-weight: bold; color: #dc3545;")
        layout_grupo.addWidget(label_nombre_servicio)
        
        self.campo_nombre_servicio = QLineEdit()
        self.campo_nombre_servicio.setPlaceholderText("Ingrese el nombre del servicio (obligatorio)")
        self.campo_nombre_servicio.setStyleSheet("border: 2px solid #dc3545;")
        self.campo_nombre_servicio.textChanged.connect(self._validar_campo_nombre)
        layout_grupo.addWidget(self.campo_nombre_servicio)
        
        # Campo para tamaño de fuente del texto
        layout_tamano_fuente = QHBoxLayout()
        label_tamano_fuente = QLabel("Tamaño de fuente (px):")
        label_tamano_fuente.setStyleSheet("font-weight: bold;")
        layout_tamano_fuente.addWidget(label_tamano_fuente)
        
        self.spin_tamano_fuente = QSpinBox()
        self.spin_tamano_fuente.setMinimum(10)
        self.spin_tamano_fuente.setMaximum(50)
        self.spin_tamano_fuente.setValue(50)  # Valor por defecto: 50px
        self.spin_tamano_fuente.setSuffix(" px")
        self.spin_tamano_fuente.setToolTip("Tamaño de la fuente del nombre del servicio debajo del código de barras (10-50 píxeles)")
        layout_tamano_fuente.addWidget(self.spin_tamano_fuente)
        layout_tamano_fuente.addStretch()
        layout_grupo.addLayout(layout_tamano_fuente)
        
        separador1 = QLabel("─────────────────────────────────────")
        separador1.setStyleSheet("color: #ccc;")
        layout_grupo.addWidget(separador1)
        
        self.label_id_generado = QLabel()
        self.label_id_generado.setStyleSheet(
            "color: #0066cc; font-size: 10pt; font-weight: bold; "
            "padding: 5px; background-color: #f0f0f0; border: 1px solid #ccc;"
        )
        layout_grupo.addWidget(self.label_id_generado)
        
        self.boton_generar = QPushButton("Generar Código de Barras")
        self.boton_generar.setMinimumHeight(40)
        layout_grupo.addWidget(self.boton_generar)
        
        separador2 = QLabel("─────────────────────────────────────")
        separador2.setStyleSheet("color: #ccc;")
        layout_grupo.addWidget(separador2)
        
        label_descargas = QLabel("Descargas:")
        label_descargas.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout_grupo.addWidget(label_descargas)
        
        layout_botones_descarga = QHBoxLayout()
        self.boton_descargar_individual = QPushButton("Descargar Individual (PNG)")
        self.boton_descargar_individual.setMinimumHeight(35)
        self.boton_descargar_individual.setEnabled(False)
        layout_botones_descarga.addWidget(self.boton_descargar_individual)
        
        self.boton_descargar_masivo = QPushButton("Descargar Masivo (ZIP)")
        self.boton_descargar_masivo.setMinimumHeight(35)
        layout_botones_descarga.addWidget(self.boton_descargar_masivo)
        layout_grupo.addLayout(layout_botones_descarga)
        
        separador3 = QLabel("─────────────────────────────────────")
        separador3.setStyleSheet("color: #ccc;")
        layout_grupo.addWidget(separador3)
        
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
        
        layout_contenido.addWidget(grupo_principal)
        layout_contenido.addStretch()
        
        scroll_area.setWidget(widget_contenido)
        layout_formulario.addWidget(scroll_area)
        
        widget_formulario.setMinimumWidth(350)
        splitter.addWidget(widget_formulario)
        
        # Panel derecho: Tabla de servicios
        grupo_tabla = QGroupBox("Servicios Registrados")
        layout_tabla = QVBoxLayout()
        grupo_tabla.setLayout(layout_tabla)
        
        # Búsqueda
        layout_busqueda = QHBoxLayout()
        label_busqueda = QLabel("Buscar:")
        layout_busqueda.addWidget(label_busqueda)
        
        self.campo_busqueda = QLineEdit()
        self.campo_busqueda.setPlaceholderText("Buscar por nombre, código o ID único...")
        layout_busqueda.addWidget(self.campo_busqueda)
        
        self.boton_refrescar = QPushButton("Refrescar")
        layout_busqueda.addWidget(self.boton_refrescar)
        layout_tabla.addLayout(layout_busqueda)
        
        # Botones de acción para la tabla
        layout_botones_tabla = QHBoxLayout()
        
        self.boton_importar_excel = QPushButton("Importar desde Excel")
        self.boton_importar_excel.setStyleSheet("background-color: #6f42c1; color: white;")
        self.boton_importar_excel.setMinimumWidth(160)
        self.boton_importar_excel.setToolTip("Importa servicios desde un archivo Excel y genera códigos de barras automáticamente")
        layout_botones_tabla.addWidget(self.boton_importar_excel)
        
        self.boton_exportar_excel = QPushButton("Exportar a Excel")
        self.boton_exportar_excel.setStyleSheet("background-color: #17a2b8; color: white;")
        self.boton_exportar_excel.setMinimumWidth(150)
        self.boton_exportar_excel.setToolTip("Exporta todos los servicios a un archivo Excel")
        layout_botones_tabla.addWidget(self.boton_exportar_excel)
        
        self.boton_descargar_ejemplo_excel = QPushButton("Descargar Excel de Ejemplo")
        self.boton_descargar_ejemplo_excel.setStyleSheet("background-color: #ffc107; color: black;")
        self.boton_descargar_ejemplo_excel.setMinimumWidth(200)
        self.boton_descargar_ejemplo_excel.setToolTip("Descarga un archivo Excel de ejemplo con el formato esperado para importar servicios")
        layout_botones_tabla.addWidget(self.boton_descargar_ejemplo_excel)
        
        self.boton_eliminar = QPushButton("Eliminar")
        self.boton_eliminar.setStyleSheet("background-color: #dc3545; color: white;")
        self.boton_eliminar.setMinimumWidth(120)
        self.boton_eliminar.setToolTip("Elimina el/los servicio(s) seleccionado(s). Puede seleccionar múltiples servicios con Ctrl o Shift")
        layout_botones_tabla.addWidget(self.boton_eliminar)
        
        layout_botones_tabla.addStretch()
        layout_tabla.addLayout(layout_botones_tabla)
        
        # Tabla de servicios
        self.tabla_servicios = QTableWidget()
        self.tabla_servicios.setColumnCount(6)
        self.tabla_servicios.setHorizontalHeaderLabels([
            "ID", "Nombre del Servicio", "Código de Barras", "ID Único", "Fecha de Creación", "Formato"
        ])
        
        header = self.tabla_servicios.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Nombre
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Código
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # ID Único
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Fecha
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Formato
        
        self.tabla_servicios.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_servicios.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.tabla_servicios.setAlternatingRowColors(True)
        layout_tabla.addWidget(self.tabla_servicios)
        
        grupo_tabla.setMinimumWidth(500)
        splitter.addWidget(grupo_tabla)
        
        # Configurar proporciones del splitter (40% formulario, 60% tabla)
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
    
    def obtener_nombre_servicio(self) -> str:
        """
        Obtiene el nombre del servicio del formulario
        
        Returns:
            Nombre del servicio ingresado
        """
        return self.campo_nombre_servicio.text().strip()
    
    def obtener_tamano_fuente(self) -> int:
        """
        Obtiene el tamaño de fuente configurado por el usuario
        
        Returns:
            Tamaño de fuente en píxeles
        """
        return self.spin_tamano_fuente.value()
    
    def limpiar_formulario(self):
        """Limpia los campos del formulario"""
        self.campo_nombre_servicio.clear()
        self.campo_nombre_servicio.setStyleSheet("border: 2px solid #dc3545;")
        self.label_id_generado.clear()
        self.boton_descargar_individual.setEnabled(False)
    
    def actualizar_id_preview(self, siguiente_id: str):
        """
        Actualiza la vista previa del ID que se generará
        
        Args:
            siguiente_id: ID que se generará
        """
        self.label_id_generado.setText(f"ID que se generará: {siguiente_id}")
    
    def _validar_campo_nombre(self):
        """Valida y actualiza el estilo del campo de nombre de servicio"""
        texto = self.campo_nombre_servicio.text().strip()
        if texto:
            self.campo_nombre_servicio.setStyleSheet("border: 2px solid #28a745;")
        else:
            self.campo_nombre_servicio.setStyleSheet("border: 2px solid #dc3545;")
    
    def mostrar_vista_previa(self, ruta_imagen: str, informacion_imagen: dict = None):
        """
        Muestra la vista previa de la imagen
        
        Args:
            ruta_imagen: Ruta a la imagen
            informacion_imagen: Diccionario con información adicional de la imagen (opcional)
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
            
            if informacion_imagen:
                tooltip = self._generar_tooltip_informacion(informacion_imagen)
                self.label_vista_previa.setToolTip(tooltip)
            self.boton_descargar_individual.setEnabled(True)
        else:
            self.label_vista_previa.setText("Error al cargar la imagen")
    
    def _generar_tooltip_informacion(self, info: dict) -> str:
        """
        Genera un tooltip con información de la imagen
        
        Args:
            info: Diccionario con información de la imagen
            
        Returns:
            String con el tooltip formateado
        """
        lineas = []
        
        if 'dimensiones' in info:
            dims = info['dimensiones']
            lineas.append(f"Dimensiones: {dims.get('ancho', 'N/A')} x {dims.get('alto', 'N/A')} px")
        
        if 'tamano_archivo_kb' in info:
            lineas.append(f"Tamaño: {info['tamano_archivo_kb']} KB")
        
        if 'modo' in info:
            lineas.append(f"Modo: {info['modo']}")
        
        if 'calidad' in info:
            calidad = info['calidad']
            if 'resolucion_efectiva' in calidad:
                lineas.append(f"Resolución efectiva: ~{calidad['resolucion_efectiva']:.0f} DPI")
        
        return "\n".join(lineas) if lineas else "Información no disponible"
    
    def cargar_servicios(self, servicios: list):
        """
        Carga los servicios en la tabla
        
        Args:
            servicios: Lista de tuplas con los datos de los servicios
                      Formato: (id, codigo_barras, id_unico, nombre_servicio, fecha_creacion, formato, nombre_archivo)
        """
        self.tabla_servicios.setRowCount(0)
        
        for servicio in servicios:
            fila = self.tabla_servicios.rowCount()
            self.tabla_servicios.insertRow(fila)
            
            # ID
            item_id = QTableWidgetItem(str(servicio[0]))
            item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_servicios.setItem(fila, 0, item_id)
            
            # Nombre del Servicio
            item_nombre = QTableWidgetItem(servicio[3] or "")
            item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_servicios.setItem(fila, 1, item_nombre)
            
            # Código de Barras
            item_codigo = QTableWidgetItem(servicio[1] or "")
            item_codigo.setFlags(item_codigo.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_servicios.setItem(fila, 2, item_codigo)
            
            # ID Único
            item_id_unico = QTableWidgetItem(servicio[2] or "")
            item_id_unico.setFlags(item_id_unico.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_servicios.setItem(fila, 3, item_id_unico)
            
            # Fecha de Creación
            fecha_str = servicio[4] if len(servicio) > 4 and servicio[4] else ""
            item_fecha = QTableWidgetItem(fecha_str)
            item_fecha.setFlags(item_fecha.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_servicios.setItem(fila, 4, item_fecha)
            
            # Formato
            formato_str = servicio[5] if len(servicio) > 5 and servicio[5] else "Code128"
            item_formato = QTableWidgetItem(formato_str)
            item_formato.setFlags(item_formato.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_servicios.setItem(fila, 5, item_formato)
    
    def obtener_fila_seleccionada(self):
        """
        Obtiene los datos de la fila seleccionada (primera selección)
        
        Returns:
            Tupla con (id_db, codigo_barras, id_unico, nombre_servicio, formato) o None
        """
        filas_seleccionadas = self.tabla_servicios.selectedIndexes()
        if not filas_seleccionadas:
            return None
        
        fila = filas_seleccionadas[0].row()
        
        id_db = int(self.tabla_servicios.item(fila, 0).text())
        codigo_barras = self.tabla_servicios.item(fila, 2).text()
        id_unico = self.tabla_servicios.item(fila, 3).text()
        nombre_servicio = self.tabla_servicios.item(fila, 1).text()
        formato = self.tabla_servicios.item(fila, 5).text()
        
        return id_db, codigo_barras, id_unico, nombre_servicio, formato
    
    def obtener_filas_seleccionadas(self):
        """
        Obtiene los datos de todas las filas seleccionadas
        
        Returns:
            Lista de tuplas con (id_db, codigo_barras, id_unico, nombre_servicio, formato)
        """
        filas_seleccionadas = self.tabla_servicios.selectedIndexes()
        if not filas_seleccionadas:
            return []
        
        # Obtener filas únicas (puede haber múltiples índices por fila)
        filas_unicas = set()
        for index in filas_seleccionadas:
            filas_unicas.add(index.row())
        
        resultados = []
        for fila in filas_unicas:
            id_db = int(self.tabla_servicios.item(fila, 0).text())
            codigo_barras = self.tabla_servicios.item(fila, 2).text()
            id_unico = self.tabla_servicios.item(fila, 3).text()
            nombre_servicio = self.tabla_servicios.item(fila, 1).text()
            formato = self.tabla_servicios.item(fila, 5).text()
            
            resultados.append((id_db, codigo_barras, id_unico, nombre_servicio, formato))
        
        return resultados
    
    def obtener_termino_busqueda(self) -> str:
        """
        Obtiene el término de búsqueda
        
        Returns:
            Término de búsqueda
        """
        return self.campo_busqueda.text().strip()

