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
        self.tabla_empleados.setColumnCount(8)
        self.tabla_empleados.setHorizontalHeaderLabels([
            "ID", "Nombres", "Apellidos", "Código de Empleado", "ID Único", "Código de Barras", "Formato", "Archivo"
        ])
        # Hacer la tabla responsive
        header = self.tabla_empleados.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID: tamaño contenido
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Nombres: estirable
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Apellidos: estirable
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Código de Empleado: estirable
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # ID Único: estirable
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Código de Barras: estirable
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Formato: tamaño contenido
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Archivo: tamaño contenido
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
        
        self.boton_generar_individual = QPushButton("Generar Carnet Individual (PNG)")
        self.boton_generar_individual.setStyleSheet("background-color: #28a745; color: white;")
        layout_acciones.addWidget(self.boton_generar_individual)
        
        self.boton_generar_masivo = QPushButton("Generar Carnets Masivos (PNG)")
        self.boton_generar_masivo.setStyleSheet("background-color: #007bff; color: white;")
        layout_acciones.addWidget(self.boton_generar_masivo)
        
        # Botones para PDF
        self.boton_generar_individual_pdf = QPushButton("Generar Carnet Individual PDF")
        self.boton_generar_individual_pdf.setStyleSheet("background-color: #dc3545; color: white;")
        layout_acciones.addWidget(self.boton_generar_individual_pdf)
        
        self.boton_generar_masivo_pdf = QPushButton("Generar Carnets Masivos PDF")
        self.boton_generar_masivo_pdf.setStyleSheet("background-color: #fd7e14; color: white;")
        layout_acciones.addWidget(self.boton_generar_masivo_pdf)
        
        layout_acciones.addStretch()
        layout.addWidget(grupo_acciones)
    
    def cargar_empleados(self, empleados: list):
        """
        Carga la lista de empleados en la tabla
        
        Args:
            empleados: Lista de tuplas con datos de empleados de la BD
                     (id, codigo_barras, id_unico, fecha_creacion, nombres, apellidos, descripcion, formato, nombre_archivo)
        """
        self.tabla_empleados.setRowCount(len(empleados))
        
        for fila, empleado in enumerate(empleados):
            # La BD devuelve: (id, codigo_barras, id_unico, fecha_creacion, nombres, apellidos, descripcion, formato, nombre_archivo)
            if len(empleado) >= 9:
                id_db = empleado[0]
                codigo_barras = empleado[1] or ""
                id_unico = empleado[2] or ""
                fecha_creacion = empleado[3] or ""
                nombres = empleado[4] or ""
                apellidos = empleado[5] or ""
                descripcion = empleado[6] or ""
                formato = empleado[7] or ""
                nombre_archivo = empleado[8] or ""
                
                # Mapear a las columnas de la tabla: ID, Nombres, Apellidos, Código de Empleado, ID Único, Código de Barras, Formato, Archivo
                self.tabla_empleados.setItem(fila, 0, QTableWidgetItem(str(id_db)))
                self.tabla_empleados.setItem(fila, 1, QTableWidgetItem(nombres))
                self.tabla_empleados.setItem(fila, 2, QTableWidgetItem(apellidos))
                self.tabla_empleados.setItem(fila, 3, QTableWidgetItem(descripcion))  # Código de Empleado
                self.tabla_empleados.setItem(fila, 4, QTableWidgetItem(id_unico))
                self.tabla_empleados.setItem(fila, 5, QTableWidgetItem(codigo_barras))
                self.tabla_empleados.setItem(fila, 6, QTableWidgetItem(formato))
                self.tabla_empleados.setItem(fila, 7, QTableWidgetItem(nombre_archivo))
            elif len(empleado) >= 8:
                # Formato antiguo con nombre_empleado (retrocompatibilidad)
                id_db = empleado[0]
                codigo_barras = empleado[1] or ""
                id_unico = empleado[2] or ""
                fecha_creacion = empleado[3] or ""
                nombre_empleado = empleado[4] or ""
                descripcion = empleado[5] or ""
                formato = empleado[6] or ""
                nombre_archivo = empleado[7] or ""
                
                # Dividir nombre_empleado en nombres y apellidos
                partes = nombre_empleado.strip().split()
                if len(partes) <= 1:
                    nombres = nombre_empleado
                    apellidos = ""
                else:
                    nombres = partes[0]
                    apellidos = " ".join(partes[1:])
                
                self.tabla_empleados.setItem(fila, 0, QTableWidgetItem(str(id_db)))
                self.tabla_empleados.setItem(fila, 1, QTableWidgetItem(nombres))
                self.tabla_empleados.setItem(fila, 2, QTableWidgetItem(apellidos))
                self.tabla_empleados.setItem(fila, 3, QTableWidgetItem(descripcion))
                self.tabla_empleados.setItem(fila, 4, QTableWidgetItem(id_unico))
                self.tabla_empleados.setItem(fila, 5, QTableWidgetItem(codigo_barras))
                self.tabla_empleados.setItem(fila, 6, QTableWidgetItem(formato))
                self.tabla_empleados.setItem(fila, 7, QTableWidgetItem(nombre_archivo))
    
    def obtener_empleado_seleccionado(self):
        """
        Obtiene el empleado seleccionado
        
        Returns:
            Tupla con (id, codigo_barras, id_unico, nombres, apellidos, descripcion, formato, nombre_archivo) o None
        """
        fila = self.tabla_empleados.currentRow()
        if fila < 0:
            return None
        
        id_db = int(self.tabla_empleados.item(fila, 0).text())
        nombres = self.tabla_empleados.item(fila, 1).text()
        apellidos = self.tabla_empleados.item(fila, 2).text()
        codigo_empleado = self.tabla_empleados.item(fila, 3).text()  # Código de Empleado (descripcion)
        id_unico = self.tabla_empleados.item(fila, 4).text()
        codigo_barras = self.tabla_empleados.item(fila, 5).text()
        formato = self.tabla_empleados.item(fila, 6).text()
        nombre_archivo = self.tabla_empleados.item(fila, 7).text()
        
        return id_db, codigo_barras, id_unico, nombres, apellidos, codigo_empleado, formato, nombre_archivo
    
    def obtener_empleados_seleccionados(self):
        """
        Obtiene todos los empleados seleccionados
        
        Returns:
            Lista de tuplas con datos de empleados en formato:
            (id, codigo_barras, id_unico, fecha_creacion, nombres, apellidos, descripcion, formato, nombre_archivo)
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
            nombres = self.tabla_empleados.item(fila, 1).text()
            apellidos = self.tabla_empleados.item(fila, 2).text()
            codigo_empleado = self.tabla_empleados.item(fila, 3).text()  # Código de Empleado (descripcion)
            id_unico = self.tabla_empleados.item(fila, 4).text()
            codigo_barras = self.tabla_empleados.item(fila, 5).text()
            formato = self.tabla_empleados.item(fila, 6).text()
            nombre_archivo = self.tabla_empleados.item(fila, 7).text()
            
            # Formato completo: (id, codigo_barras, id_unico, fecha_creacion, nombres, apellidos, descripcion, formato, nombre_archivo)
            # fecha_creacion no está en la tabla, usar cadena vacía
            resultados.append((id_db, codigo_barras, id_unico, "", nombres, apellidos, codigo_empleado, formato, nombre_archivo))
        
        return resultados
    
    def obtener_todos_empleados(self):
        """
        Obtiene todos los empleados de la tabla (sin importar si están seleccionados o no)
        
        Returns:
            Lista de tuplas con datos de empleados en formato:
            (id, codigo_barras, id_unico, fecha_creacion, nombres, apellidos, descripcion, formato, nombre_archivo)
        """
        resultados = []
        total_filas = self.tabla_empleados.rowCount()
        
        for fila in range(total_filas):
            id_db = int(self.tabla_empleados.item(fila, 0).text())
            nombres = self.tabla_empleados.item(fila, 1).text()
            apellidos = self.tabla_empleados.item(fila, 2).text()
            codigo_empleado = self.tabla_empleados.item(fila, 3).text()  # Código de Empleado (descripcion)
            id_unico = self.tabla_empleados.item(fila, 4).text()
            codigo_barras = self.tabla_empleados.item(fila, 5).text()
            formato = self.tabla_empleados.item(fila, 6).text()
            nombre_archivo = self.tabla_empleados.item(fila, 7).text()
            
            # Formato completo: (id, codigo_barras, id_unico, fecha_creacion, nombres, apellidos, descripcion, formato, nombre_archivo)
            # fecha_creacion no está en la tabla, usar cadena vacía
            resultados.append((id_db, codigo_barras, id_unico, "", nombres, apellidos, codigo_empleado, formato, nombre_archivo))
        
        return resultados
    
    def obtener_termino_busqueda(self) -> str:
        """Obtiene el término de búsqueda"""
        return self.campo_busqueda.text().strip()

