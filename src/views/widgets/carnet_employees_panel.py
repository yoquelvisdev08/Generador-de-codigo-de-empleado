"""
Panel de lista de empleados y acciones para carnets
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QGroupBox, QHeaderView,
                             QLabel, QLineEdit, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from pathlib import Path


class CarnetEmployeesPanel(QWidget):
    """Panel para listar empleados y generar carnets"""
    
    def __init__(self, parent=None):
        """
        Inicializa el panel de empleados
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Grupo: Lista de Empleados
        grupo_lista = QGroupBox("Empleados con Códigos de Barras")
        layout_lista = QVBoxLayout()
        grupo_lista.setLayout(layout_lista)
        
        # Búsqueda
        layout_busqueda = QHBoxLayout()
        label_busqueda = QLabel("Buscar:")
        self.campo_busqueda = QLineEdit()
        self.campo_busqueda.setPlaceholderText("Buscar por nombre o código...")
        layout_busqueda.addWidget(label_busqueda)
        layout_busqueda.addWidget(self.campo_busqueda)
        layout_lista.addLayout(layout_busqueda)
        
        # Tabla de empleados con scroll
        self.tabla_empleados = QTableWidget()
        self.tabla_empleados.setColumnCount(7)
        self.tabla_empleados.setHorizontalHeaderLabels([
            "ID", "Nombre del Empleado", "Código de Empleado", "ID Único", "Código de Barras", "Formato", "Archivo"
        ])
        # Hacer la tabla responsive
        header = self.tabla_empleados.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID: tamaño contenido
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Nombre: estirable
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Código de Empleado: estirable
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # ID Único: estirable
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Código de Barras: estirable
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Formato: tamaño contenido
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Archivo: tamaño contenido
        self.tabla_empleados.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_empleados.setSelectionMode(
            QTableWidget.SelectionMode.ExtendedSelection
        )
        self.tabla_empleados.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        # Habilitar scroll vertical y horizontal
        self.tabla_empleados.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tabla_empleados.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Permitir que la tabla muestre todas las filas con scroll
        self.tabla_empleados.setAlternatingRowColors(True)  # Colores alternados para mejor legibilidad
        layout_lista.addWidget(self.tabla_empleados)
        
        layout.addWidget(grupo_lista)
        
        # Grupo: Acciones
        grupo_acciones = QGroupBox("Acciones")
        layout_acciones = QHBoxLayout()
        grupo_acciones.setLayout(layout_acciones)
        
        self.boton_vista_previa = QPushButton("Vista Previa")
        self.boton_vista_previa.setStyleSheet("background-color: #17a2b8; color: white;")
        layout_acciones.addWidget(self.boton_vista_previa)
        
        self.boton_generar_individual = QPushButton("Generar Carnet Individual")
        self.boton_generar_individual.setStyleSheet("background-color: #28a745; color: white;")
        layout_acciones.addWidget(self.boton_generar_individual)
        
        self.boton_generar_masivo = QPushButton("Generar Carnets Masivos")
        self.boton_generar_masivo.setStyleSheet("background-color: #007bff; color: white;")
        layout_acciones.addWidget(self.boton_generar_masivo)
        
        self.boton_exportar = QPushButton("Exportar Carnets")
        self.boton_exportar.setStyleSheet("background-color: #ffc107; color: black;")
        layout_acciones.addWidget(self.boton_exportar)
        
        layout_acciones.addStretch()
        layout.addWidget(grupo_acciones)
    
    def cargar_empleados(self, empleados: list):
        """
        Carga la lista de empleados en la tabla
        
        Args:
            empleados: Lista de tuplas con datos de empleados de la BD
                     (id, codigo_barras, id_unico, fecha_creacion, nombre_empleado, descripcion, formato, nombre_archivo)
        """
        self.tabla_empleados.setRowCount(len(empleados))
        
        for fila, empleado in enumerate(empleados):
            # La BD devuelve: (id, codigo_barras, id_unico, fecha_creacion, nombre_empleado, descripcion, formato, nombre_archivo)
            if len(empleado) >= 8:
                id_db = empleado[0]
                codigo_barras = empleado[1] or ""
                id_unico = empleado[2] or ""
                fecha_creacion = empleado[3] or ""
                nombre_empleado = empleado[4] or ""
                descripcion = empleado[5] or ""
                formato = empleado[6] or ""
                nombre_archivo = empleado[7] or ""
                
                # Mapear a las columnas de la tabla: ID, Nombre, Código de Empleado, ID Único, Código de Barras, Formato, Archivo
                self.tabla_empleados.setItem(fila, 0, QTableWidgetItem(str(id_db)))
                self.tabla_empleados.setItem(fila, 1, QTableWidgetItem(nombre_empleado))
                self.tabla_empleados.setItem(fila, 2, QTableWidgetItem(descripcion))  # Código de Empleado
                self.tabla_empleados.setItem(fila, 3, QTableWidgetItem(id_unico))
                self.tabla_empleados.setItem(fila, 4, QTableWidgetItem(codigo_barras))
                self.tabla_empleados.setItem(fila, 5, QTableWidgetItem(formato))
                self.tabla_empleados.setItem(fila, 6, QTableWidgetItem(nombre_archivo))
            elif len(empleado) >= 6:
                # Compatibilidad con formato anterior
                id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = empleado[:6]
                
                self.tabla_empleados.setItem(fila, 0, QTableWidgetItem(str(id_db)))
                self.tabla_empleados.setItem(fila, 1, QTableWidgetItem(nombre_empleado or ""))
                self.tabla_empleados.setItem(fila, 2, QTableWidgetItem(""))  # Código de Empleado (vacío si no está disponible)
                self.tabla_empleados.setItem(fila, 3, QTableWidgetItem(id_unico or ""))
                self.tabla_empleados.setItem(fila, 4, QTableWidgetItem(codigo_barras or ""))
                self.tabla_empleados.setItem(fila, 5, QTableWidgetItem(formato or ""))
                self.tabla_empleados.setItem(fila, 6, QTableWidgetItem(nombre_archivo or ""))
    
    def obtener_empleado_seleccionado(self):
        """
        Obtiene el empleado seleccionado
        
        Returns:
            Tupla con (id, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo) o None
        """
        fila = self.tabla_empleados.currentRow()
        if fila < 0:
            return None
        
        id_db = int(self.tabla_empleados.item(fila, 0).text())
        nombre_empleado = self.tabla_empleados.item(fila, 1).text()
        codigo_empleado = self.tabla_empleados.item(fila, 2).text()  # Código de Empleado
        id_unico = self.tabla_empleados.item(fila, 3).text()
        codigo_barras = self.tabla_empleados.item(fila, 4).text()
        formato = self.tabla_empleados.item(fila, 5).text()
        nombre_archivo = self.tabla_empleados.item(fila, 6).text()
        
        return id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo
    
    def obtener_empleados_seleccionados(self):
        """
        Obtiene todos los empleados seleccionados
        
        Returns:
            Lista de tuplas con datos de empleados
        """
        filas_seleccionadas = self.tabla_empleados.selectedIndexes()
        if not filas_seleccionadas:
            return []
        
        filas_unicas = set()
        for index in filas_seleccionadas:
            filas_unicas.add(index.row())
        
        resultados = []
        for fila in filas_unicas:
            id_db = int(self.tabla_empleados.item(fila, 0).text())
            nombre_empleado = self.tabla_empleados.item(fila, 1).text()
            codigo_empleado = self.tabla_empleados.item(fila, 2).text()  # Código de Empleado
            id_unico = self.tabla_empleados.item(fila, 3).text()
            codigo_barras = self.tabla_empleados.item(fila, 4).text()
            formato = self.tabla_empleados.item(fila, 5).text()
            nombre_archivo = self.tabla_empleados.item(fila, 6).text()
            
            resultados.append((id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo))
        
        return resultados
    
    def obtener_termino_busqueda(self) -> str:
        """Obtiene el término de búsqueda"""
        return self.campo_busqueda.text().strip()

