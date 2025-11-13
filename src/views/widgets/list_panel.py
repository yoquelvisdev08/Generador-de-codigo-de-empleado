"""
Panel de listado de códigos de barras
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QGroupBox, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt


class ListPanel(QWidget):
    """Panel para listar y gestionar códigos de barras"""
    
    def __init__(self, parent=None):
        """
        Inicializa el panel de listado
        
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
        
        grupo_busqueda = QGroupBox("Búsqueda y Filtros")
        layout_busqueda = QHBoxLayout()
        grupo_busqueda.setLayout(layout_busqueda)
        
        label_busqueda = QLabel("Buscar:")
        layout_busqueda.addWidget(label_busqueda)
        
        self.campo_busqueda = QLineEdit()
        self.campo_busqueda.setPlaceholderText("Buscar por código, ID único o código de empleado...")
        layout_busqueda.addWidget(self.campo_busqueda)
        
        self.boton_refrescar = QPushButton("Refrescar")
        layout_busqueda.addWidget(self.boton_refrescar)
        
        layout.addWidget(grupo_busqueda)
        
        # Botones de acción debajo del buscador - organizados en 3 filas de 3 botones cada una
        contenedor_botones = QVBoxLayout()
        contenedor_botones.setSpacing(8)  # Espacio vertical entre filas
        
        # Primera fila de botones (3 botones)
        fila1 = QHBoxLayout()
        fila1.setSpacing(10)  # Espacio horizontal entre botones
        
        self.boton_exportar = QPushButton("Exportar Seleccionados")
        self.boton_exportar.setMinimumWidth(150)
        fila1.addWidget(self.boton_exportar)
        
        self.boton_exportar_todos = QPushButton("Exportar Todos (ZIP)")
        self.boton_exportar_todos.setMinimumWidth(150)
        fila1.addWidget(self.boton_exportar_todos)
        
        self.boton_exportar_excel = QPushButton("Exportar Data en Excel")
        self.boton_exportar_excel.setStyleSheet("background-color: #17a2b8; color: white;")
        self.boton_exportar_excel.setMinimumWidth(160)
        self.boton_exportar_excel.setToolTip("Exporta todos los datos de la base de datos a un archivo Excel")
        fila1.addWidget(self.boton_exportar_excel)
        
        fila1.addStretch()  # Empujar botones hacia la izquierda
        contenedor_botones.addLayout(fila1)
        
        # Segunda fila de botones (3 botones)
        fila2 = QHBoxLayout()
        fila2.setSpacing(10)
        
        self.boton_importar_excel = QPushButton("Importar Data en Excel")
        self.boton_importar_excel.setStyleSheet("background-color: #6f42c1; color: white;")
        self.boton_importar_excel.setMinimumWidth(160)
        self.boton_importar_excel.setToolTip("Importa datos desde un archivo Excel y genera códigos de barras automáticamente")
        fila2.addWidget(self.boton_importar_excel)
        
        self.boton_descargar_ejemplo_excel = QPushButton("Descargar Excel de Ejemplo")
        self.boton_descargar_ejemplo_excel.setStyleSheet("background-color: #ffc107; color: black;")
        self.boton_descargar_ejemplo_excel.setMinimumWidth(200)
        self.boton_descargar_ejemplo_excel.setToolTip("Descarga un archivo Excel de ejemplo con el formato esperado para importar datos")
        fila2.addWidget(self.boton_descargar_ejemplo_excel)
        
        self.boton_backup = QPushButton("Backup BD")
        self.boton_backup.setStyleSheet("background-color: #28a745; color: white;")
        self.boton_backup.setMinimumWidth(120)
        fila2.addWidget(self.boton_backup)
        
        fila2.addStretch()  # Empujar botones hacia la izquierda
        contenedor_botones.addLayout(fila2)
        
        # Tercera fila de botones (3 botones)
        fila3 = QHBoxLayout()
        fila3.setSpacing(10)
        
        self.boton_eliminar = QPushButton("Eliminar")
        self.boton_eliminar.setStyleSheet("background-color: #dc3545; color: white;")
        self.boton_eliminar.setMinimumWidth(120)
        fila3.addWidget(self.boton_eliminar)
        
        self.boton_limpiar = QPushButton("Limpiar Base de Datos")
        self.boton_limpiar.setStyleSheet("background-color: #ff8800; color: white;")
        self.boton_limpiar.setMinimumWidth(180)
        fila3.addWidget(self.boton_limpiar)
        
        self.boton_limpiar_imagenes = QPushButton("Limpiar Imágenes Huérfanas")
        self.boton_limpiar_imagenes.setStyleSheet("background-color: #6c757d; color: white;")
        self.boton_limpiar_imagenes.setMinimumWidth(200)
        self.boton_limpiar_imagenes.setToolTip(
            "Elimina imágenes que no tienen registro en la base de datos"
        )
        fila3.addWidget(self.boton_limpiar_imagenes)
        
        fila3.addStretch()  # Empujar botones hacia la izquierda
        contenedor_botones.addLayout(fila3)
        
        layout.addLayout(contenedor_botones)
        
        grupo_listado = QGroupBox("Códigos Generados")
        layout_listado = QVBoxLayout()
        grupo_listado.setLayout(layout_listado)
        
        self.tabla_codigos = QTableWidget()
        self.tabla_codigos.setColumnCount(7)
        self.tabla_codigos.setHorizontalHeaderLabels([
            "ID", "Código de Barras", "ID Único", "Formato",
            "Nombre del Empleado", "Código de Empleado", "Fecha"
        ])
        # Hacer la tabla responsive: algunas columnas fijas, otras estirables
        header = self.tabla_codigos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID: tamaño contenido
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Código: estirable
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # ID Único: estirable
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Formato: tamaño contenido
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Nombre: estirable
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Código de Empleado: estirable
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Fecha: tamaño contenido
        self.tabla_codigos.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_codigos.setSelectionMode(
            QTableWidget.SelectionMode.ExtendedSelection
        )
        self.tabla_codigos.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        
        layout_listado.addWidget(self.tabla_codigos)
        
        layout.addWidget(grupo_listado)
        
        # Por defecto, los botones de admin están visibles
        # Se ocultarán si el usuario no es admin mediante configurar_permisos
        self.es_admin = True
    
    def cargar_codigos(self, codigos: list):
        """
        Carga códigos en la tabla
        
        Args:
            codigos: Lista de tuplas con los datos de los códigos
        """
        self.tabla_codigos.setRowCount(len(codigos))
        
        for fila, codigo in enumerate(codigos):
            if len(codigo) == 8:
                id_db, codigo_barras, id_unico, fecha, nombre_empleado, descripcion, formato, nombre_archivo = codigo
            else:
                # Compatibilidad con formato anterior (sin nombre_archivo)
                id_db, codigo_barras, id_unico, fecha, nombre_empleado, descripcion, formato = codigo
                nombre_archivo = ""
            
            self.tabla_codigos.setItem(fila, 0, QTableWidgetItem(str(id_db)))
            self.tabla_codigos.setItem(fila, 1, QTableWidgetItem(codigo_barras))
            self.tabla_codigos.setItem(fila, 2, QTableWidgetItem(id_unico))
            self.tabla_codigos.setItem(fila, 3, QTableWidgetItem(formato))
            self.tabla_codigos.setItem(fila, 4, QTableWidgetItem(nombre_empleado or ""))
            self.tabla_codigos.setItem(fila, 5, QTableWidgetItem(descripcion or ""))
            self.tabla_codigos.setItem(fila, 6, QTableWidgetItem(fecha))
    
    def obtener_fila_seleccionada(self):
        """
        Obtiene los datos de la fila seleccionada
        
        Returns:
            Tupla con (id_db, codigo_barras, id_unico, formato, nombre_archivo) o None
        """
        fila = self.tabla_codigos.currentRow()
        if fila < 0:
            return None
        
        id_db = int(self.tabla_codigos.item(fila, 0).text())
        codigo_barras = self.tabla_codigos.item(fila, 1).text()
        id_unico = self.tabla_codigos.item(fila, 2).text()
        formato = self.tabla_codigos.item(fila, 3).text()
        nombre_empleado = self.tabla_codigos.item(fila, 4).text()
        
        # Generar nombre_archivo dinámicamente (no se muestra en la tabla)
        from src.utils.file_utils import limpiar_nombre_archivo
        nombre_empleado_limpio = limpiar_nombre_archivo(nombre_empleado or "sin_nombre")
        nombre_archivo = f"{nombre_empleado_limpio}_{codigo_barras}.png"
        
        return id_db, codigo_barras, id_unico, formato, nombre_archivo
    
    def obtener_filas_seleccionadas(self):
        """
        Obtiene los datos de todas las filas seleccionadas
        
        Returns:
            Lista de tuplas con (id_db, codigo_barras, id_unico, formato, nombre_empleado)
        """
        filas_seleccionadas = self.tabla_codigos.selectedIndexes()
        if not filas_seleccionadas:
            return []
        
        filas_unicas = set()
        for index in filas_seleccionadas:
            filas_unicas.add(index.row())
        
        resultados = []
        from src.utils.file_utils import limpiar_nombre_archivo
        for fila in filas_unicas:
            id_db = int(self.tabla_codigos.item(fila, 0).text())
            codigo_barras = self.tabla_codigos.item(fila, 1).text()
            id_unico = self.tabla_codigos.item(fila, 2).text()
            formato = self.tabla_codigos.item(fila, 3).text()
            nombre_empleado = self.tabla_codigos.item(fila, 4).text()
            # Generar nombre_archivo dinámicamente (no se muestra en la tabla)
            nombre_empleado_limpio = limpiar_nombre_archivo(nombre_empleado or "sin_nombre")
            nombre_archivo = f"{nombre_empleado_limpio}_{codigo_barras}.png"
            resultados.append((id_db, codigo_barras, id_unico, formato, nombre_empleado, nombre_archivo))
        
        return resultados
    
    def obtener_termino_busqueda(self) -> str:
        """
        Obtiene el término de búsqueda
        
        Returns:
            Término de búsqueda
        """
        return self.campo_busqueda.text().strip()
    
    def configurar_permisos(self, es_admin: bool = True):
        """
        Configura la visibilidad de los botones según los permisos del usuario
        
        Args:
            es_admin: Si True, muestra los botones de administración. Si False, los oculta.
        """
        self.es_admin = es_admin
        
        # Botones que solo los administradores pueden ver
        # - Backup BD
        # - Limpiar Base de Datos
        # - Limpiar Imágenes Huérfanas
        self.boton_backup.setVisible(es_admin)
        self.boton_limpiar.setVisible(es_admin)
        self.boton_limpiar_imagenes.setVisible(es_admin)

