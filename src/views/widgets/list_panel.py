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
        self.setLayout(layout)
        
        grupo_busqueda = QGroupBox("Búsqueda y Filtros")
        layout_busqueda = QHBoxLayout()
        grupo_busqueda.setLayout(layout_busqueda)
        
        label_busqueda = QLabel("Buscar:")
        layout_busqueda.addWidget(label_busqueda)
        
        self.campo_busqueda = QLineEdit()
        self.campo_busqueda.setPlaceholderText("Buscar por código, ID único o descripción...")
        layout_busqueda.addWidget(self.campo_busqueda)
        
        self.boton_refrescar = QPushButton("Refrescar")
        layout_busqueda.addWidget(self.boton_refrescar)
        
        layout.addWidget(grupo_busqueda)
        
        grupo_listado = QGroupBox("Códigos Generados")
        layout_listado = QVBoxLayout()
        grupo_listado.setLayout(layout_listado)
        
        self.tabla_codigos = QTableWidget()
        self.tabla_codigos.setColumnCount(7)
        self.tabla_codigos.setHorizontalHeaderLabels([
            "ID", "Código de Barras", "ID Único", "Formato",
            "Nombre del Empleado", "Descripción", "Fecha"
        ])
        self.tabla_codigos.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
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
        
        layout_botones = QHBoxLayout()
        
        self.boton_ver_imagen = QPushButton("Ver Imagen")
        layout_botones.addWidget(self.boton_ver_imagen)
        
        self.boton_exportar = QPushButton("Exportar Seleccionados")
        layout_botones.addWidget(self.boton_exportar)
        
        self.boton_exportar_todos = QPushButton("Exportar Todos (ZIP)")
        layout_botones.addWidget(self.boton_exportar_todos)
        
        self.boton_backup = QPushButton("Backup BD")
        self.boton_backup.setStyleSheet("background-color: #28a745; color: white;")
        layout_botones.addWidget(self.boton_backup)
        
        self.boton_eliminar = QPushButton("Eliminar")
        self.boton_eliminar.setStyleSheet("background-color: #dc3545; color: white;")
        layout_botones.addWidget(self.boton_eliminar)
        
        self.boton_limpiar = QPushButton("Limpiar Base de Datos")
        self.boton_limpiar.setStyleSheet("background-color: #ff8800; color: white;")
        layout_botones.addWidget(self.boton_limpiar)
        
        layout_botones.addStretch()
        layout_listado.addLayout(layout_botones)
        
        layout.addWidget(grupo_listado)
    
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
                id_db, codigo_barras, id_unico, fecha, nombre_empleado, descripcion, formato = codigo
            
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
        for fila in filas_unicas:
            id_db = int(self.tabla_codigos.item(fila, 0).text())
            codigo_barras = self.tabla_codigos.item(fila, 1).text()
            id_unico = self.tabla_codigos.item(fila, 2).text()
            formato = self.tabla_codigos.item(fila, 3).text()
            nombre_empleado = self.tabla_codigos.item(fila, 4).text()
            resultados.append((id_db, codigo_barras, id_unico, formato, nombre_empleado))
        
        return resultados
    
    def obtener_termino_busqueda(self) -> str:
        """
        Obtiene el término de búsqueda
        
        Returns:
            Término de búsqueda
        """
        return self.campo_busqueda.text().strip()

