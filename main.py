import sys
import os
import zipfile
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QComboBox, QTextEdit, QTableWidget, QTableWidgetItem,
                             QMessageBox, QGroupBox, QFileDialog, QHeaderView,
                             QSplitter, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont
from database import DatabaseManager
from barcode_generator import GeneradorCodigoBarras


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.generador = GeneradorCodigoBarras()
        self.init_ui()
        self.cargar_codigos_existentes()
    
    def init_ui(self):
        self.setWindowTitle("Generador de Códigos de Barras - by yoquelvisdev")
        self.setGeometry(100, 100, 1200, 800)
        
        widget_principal = QWidget()
        self.setCentralWidget(widget_principal)
        
        layout_principal = QVBoxLayout()
        widget_principal.setLayout(layout_principal)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout_principal.addWidget(splitter)
        
        panel_izquierdo = self.crear_panel_generacion()
        panel_derecho = self.crear_panel_listado()
        
        splitter.addWidget(panel_izquierdo)
        splitter.addWidget(panel_derecho)
        splitter.setSizes([400, 800])
        
        self.crear_barra_estado()
        self.actualizar_id_preview()
    
    def crear_panel_generacion(self):
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        grupo_generacion = QGroupBox("Generar Nuevo Código de Barras")
        layout_grupo = QVBoxLayout()
        grupo_generacion.setLayout(layout_grupo)
        
        label_formato = QLabel("Formato:")
        layout_grupo.addWidget(label_formato)
        
        self.combo_formato = QComboBox()
        self.combo_formato.addItems(self.generador.obtener_formatos_disponibles())
        layout_grupo.addWidget(self.combo_formato)
        
        label_nombre = QLabel("Nombre del Empleado:")
        layout_grupo.addWidget(label_nombre)
        
        self.campo_nombre_empleado = QLineEdit()
        self.campo_nombre_empleado.setPlaceholderText("Ejemplo: Juan Pérez")
        layout_grupo.addWidget(self.campo_nombre_empleado)
        
        self.label_id_generado = QLabel()
        self.label_id_generado.setStyleSheet("color: #0066cc; font-size: 10pt; font-weight: bold; padding: 5px; background-color: #f0f0f0; border: 1px solid #ccc;")
        self.actualizar_id_preview()
        layout_grupo.addWidget(self.label_id_generado)
        
        label_descripcion = QLabel("Descripción (opcional):")
        layout_grupo.addWidget(label_descripcion)
        
        self.campo_descripcion = QLineEdit()
        self.campo_descripcion.setPlaceholderText("Descripción del código")
        layout_grupo.addWidget(self.campo_descripcion)
        
        boton_generar = QPushButton("Generar Código de Barras")
        boton_generar.setMinimumHeight(40)
        boton_generar.clicked.connect(self.generar_codigo)
        layout_grupo.addWidget(boton_generar)
        
        layout.addWidget(grupo_generacion)
        
        grupo_vista_previa = QGroupBox("Vista Previa")
        layout_vista = QVBoxLayout()
        grupo_vista_previa.setLayout(layout_vista)
        
        self.label_vista_previa = QLabel()
        self.label_vista_previa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_vista_previa.setMinimumHeight(200)
        self.label_vista_previa.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        self.label_vista_previa.setText("La vista previa aparecerá aquí")
        layout_vista.addWidget(self.label_vista_previa)
        
        layout.addWidget(grupo_vista_previa)
        
        layout.addStretch()
        
        return panel
    
    def crear_panel_listado(self):
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        grupo_busqueda = QGroupBox("Búsqueda y Filtros")
        layout_busqueda = QHBoxLayout()
        grupo_busqueda.setLayout(layout_busqueda)
        
        label_busqueda = QLabel("Buscar:")
        layout_busqueda.addWidget(label_busqueda)
        
        self.campo_busqueda = QLineEdit()
        self.campo_busqueda.setPlaceholderText("Buscar por código, ID único o descripción...")
        self.campo_busqueda.textChanged.connect(self.buscar_codigos)
        layout_busqueda.addWidget(self.campo_busqueda)
        
        boton_refrescar = QPushButton("Refrescar")
        boton_refrescar.clicked.connect(self.cargar_codigos_existentes)
        layout_busqueda.addWidget(boton_refrescar)
        
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
        self.tabla_codigos.doubleClicked.connect(self.mostrar_detalle_codigo)
        
        layout_listado.addWidget(self.tabla_codigos)
        
        layout_botones = QHBoxLayout()
        
        boton_ver_imagen = QPushButton("Ver Imagen")
        boton_ver_imagen.clicked.connect(self.ver_imagen_codigo)
        layout_botones.addWidget(boton_ver_imagen)
        
        boton_exportar = QPushButton("Exportar Seleccionados")
        boton_exportar.clicked.connect(self.exportar_seleccionados)
        layout_botones.addWidget(boton_exportar)
        
        boton_exportar_todos = QPushButton("Exportar Todos (ZIP)")
        boton_exportar_todos.clicked.connect(self.exportar_todos_zip)
        layout_botones.addWidget(boton_exportar_todos)
        
        boton_backup = QPushButton("Backup BD")
        boton_backup.clicked.connect(self.backup_base_datos)
        boton_backup.setStyleSheet("background-color: #28a745; color: white;")
        layout_botones.addWidget(boton_backup)
        
        boton_eliminar = QPushButton("Eliminar")
        boton_eliminar.clicked.connect(self.eliminar_codigo)
        boton_eliminar.setStyleSheet("background-color: #dc3545; color: white;")
        layout_botones.addWidget(boton_eliminar)
        
        boton_limpiar = QPushButton("Limpiar Base de Datos")
        boton_limpiar.clicked.connect(self.limpiar_base_datos)
        boton_limpiar.setStyleSheet("background-color: #ff8800; color: white;")
        layout_botones.addWidget(boton_limpiar)
        
        layout_botones.addStretch()
        layout_listado.addLayout(layout_botones)
        
        layout.addWidget(grupo_listado)
        
        return panel
    
    def crear_barra_estado(self):
        self.statusBar().showMessage("Listo")
        self.statusBar().addPermanentWidget(QLabel("by yoquelvisdev"))
        self.actualizar_estadisticas()
    
    def actualizar_id_preview(self):
        siguiente_id = self.db_manager.obtener_siguiente_id_secuencial()
        self.label_id_generado.setText(f"ID que se generará: {siguiente_id}")
    
    def actualizar_estadisticas(self):
        estadisticas = self.db_manager.obtener_estadisticas()
        mensaje = f"Total de códigos: {estadisticas['total_codigos']} | Formatos: {estadisticas['formatos_diferentes']}"
        self.statusBar().showMessage(mensaje)
    
    def generar_codigo(self):
        nombre_empleado = self.campo_nombre_empleado.text().strip()
        formato = self.combo_formato.currentText()
        descripcion = self.campo_descripcion.text().strip() or None
        
        if not nombre_empleado:
            QMessageBox.warning(self, "Advertencia", 
                              "Por favor ingrese el nombre del empleado")
            return
        
        try:
            id_unico_generado = self.db_manager.obtener_siguiente_id_secuencial()
            
            codigo_barras, id_unico_archivo, ruta_imagen = self.generador.generar_codigo_barras(
                id_unico_generado, formato, id_unico_generado, nombre_empleado
            )
            
            valido, mensaje_error = self.generador.validar_codigo_barras(ruta_imagen, id_unico_generado)
            
            if not valido:
                if os.path.exists(ruta_imagen):
                    os.remove(ruta_imagen)
                QMessageBox.critical(
                    self, "Error de Validación",
                    f"El código de barras generado no es válido:\n{mensaje_error}\n\n"
                    f"El código no se ha guardado. Por favor intente generar nuevamente."
                )
                return
            
            nombre_archivo = os.path.basename(ruta_imagen)
            
            exito = self.db_manager.insertar_codigo(
                codigo_barras, id_unico_generado, formato, nombre_empleado, descripcion, nombre_archivo
            )
            
            if not exito:
                if os.path.exists(ruta_imagen):
                    os.remove(ruta_imagen)
                QMessageBox.warning(
                    self, "Error",
                    "No se pudo guardar el código en la base de datos.\n"
                    "Puede que el ID único ya exista."
                )
                return
            
            self.mostrar_vista_previa(ruta_imagen)
            self.cargar_codigos_existentes()
            self.actualizar_estadisticas()
            self.actualizar_id_preview()
            
            self.campo_nombre_empleado.clear()
            self.campo_descripcion.clear()
            
            QMessageBox.information(
                self, "Éxito",
                f"Código de barras generado y validado exitosamente.\n"
                f"ID Único: {id_unico_generado}\n"
                f"Empleado: {nombre_empleado}\n"
                f"Validación: El código escaneado coincide con el ID generado"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Error al generar el código de barras:\n{str(e)}"
            )
    
    def mostrar_vista_previa(self, ruta_imagen: str):
        pixmap = QPixmap(ruta_imagen)
        if not pixmap.isNull():
            pixmap_escalado = pixmap.scaled(
                350, 150, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.label_vista_previa.setPixmap(pixmap_escalado)
    
    def cargar_codigos_existentes(self):
        codigos = self.db_manager.obtener_todos_codigos()
        self.tabla_codigos.setRowCount(len(codigos))
        
        for fila, codigo in enumerate(codigos):
            if len(codigo) == 8:
                id_db, codigo_barras, id_unico, fecha, nombre_empleado, descripcion, formato, nombre_archivo = codigo
            else:
                id_db, codigo_barras, id_unico, fecha, nombre_empleado, descripcion, formato = codigo
                nombre_archivo = None
            
            self.tabla_codigos.setItem(fila, 0, QTableWidgetItem(str(id_db)))
            self.tabla_codigos.setItem(fila, 1, QTableWidgetItem(codigo_barras))
            self.tabla_codigos.setItem(fila, 2, QTableWidgetItem(id_unico))
            self.tabla_codigos.setItem(fila, 3, QTableWidgetItem(formato))
            self.tabla_codigos.setItem(fila, 4, QTableWidgetItem(nombre_empleado or ""))
            self.tabla_codigos.setItem(fila, 5, QTableWidgetItem(descripcion or ""))
            self.tabla_codigos.setItem(fila, 6, QTableWidgetItem(fecha))
    
    def buscar_codigos(self):
        termino = self.campo_busqueda.text().strip()
        
        if not termino:
            self.cargar_codigos_existentes()
            return
        
        codigos = self.db_manager.buscar_codigo(termino)
        self.tabla_codigos.setRowCount(len(codigos))
        
        for fila, codigo in enumerate(codigos):
            if len(codigo) == 8:
                id_db, codigo_barras, id_unico, fecha, nombre_empleado, descripcion, formato, nombre_archivo = codigo
            else:
                id_db, codigo_barras, id_unico, fecha, nombre_empleado, descripcion, formato = codigo
                nombre_archivo = None
            
            self.tabla_codigos.setItem(fila, 0, QTableWidgetItem(str(id_db)))
            self.tabla_codigos.setItem(fila, 1, QTableWidgetItem(codigo_barras))
            self.tabla_codigos.setItem(fila, 2, QTableWidgetItem(id_unico))
            self.tabla_codigos.setItem(fila, 3, QTableWidgetItem(formato))
            self.tabla_codigos.setItem(fila, 4, QTableWidgetItem(nombre_empleado or ""))
            self.tabla_codigos.setItem(fila, 5, QTableWidgetItem(descripcion or ""))
            self.tabla_codigos.setItem(fila, 6, QTableWidgetItem(fecha))
    
    def obtener_fila_seleccionada(self):
        fila = self.tabla_codigos.currentRow()
        if fila < 0:
            return None
        
        id_db = int(self.tabla_codigos.item(fila, 0).text())
        codigo_barras = self.tabla_codigos.item(fila, 1).text()
        id_unico = self.tabla_codigos.item(fila, 2).text()
        formato = self.tabla_codigos.item(fila, 3).text()
        nombre_empleado = self.tabla_codigos.item(fila, 4).text()
        
        nombre_empleado_limpio = self.limpiar_nombre_archivo(nombre_empleado or "sin_nombre")
        nombre_archivo = f"{nombre_empleado_limpio}_{codigo_barras}.png"
        
        return id_db, codigo_barras, id_unico, formato, nombre_archivo
    
    def ver_imagen_codigo(self):
        resultado = self.obtener_fila_seleccionada()
        if resultado is None:
            QMessageBox.warning(self, "Advertencia", 
                              "Por favor seleccione un código de la tabla")
            return
        
        id_db, codigo_barras, id_unico, formato, nombre_archivo = resultado
        ruta_imagen = f"codigos_generados/{nombre_archivo}"
        
        if not os.path.exists(ruta_imagen):
            QMessageBox.warning(self, "Error", 
                              f"No se encontró la imagen del código de barras.\n"
                              f"Ruta buscada: {ruta_imagen}")
            return
        
        self.mostrar_vista_previa(ruta_imagen)
    
    def obtener_filas_seleccionadas(self):
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
    
    def limpiar_nombre_archivo(self, nombre: str) -> str:
        caracteres_invalidos = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        nombre_limpio = nombre
        for char in caracteres_invalidos:
            nombre_limpio = nombre_limpio.replace(char, '_')
        return nombre_limpio.strip()
    
    def exportar_seleccionados(self):
        filas = self.obtener_filas_seleccionadas()
        
        if not filas:
            QMessageBox.warning(self, "Advertencia", 
                              "Por favor seleccione al menos un código de la tabla")
            return
        
        directorio_destino = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta para exportar"
        )
        
        if not directorio_destino:
            return
        
        exportados = 0
        errores = 0
        
        for id_db, codigo_barras, id_unico, formato, nombre_empleado in filas:
            nombre_empleado_limpio = self.limpiar_nombre_archivo(nombre_empleado or "sin_nombre")
            nombre_archivo = f"{nombre_empleado_limpio}_{codigo_barras}.png"
            ruta_origen = f"codigos_generados/{nombre_archivo}"
            
            if not os.path.exists(ruta_origen):
                errores += 1
                continue
            
            ruta_destino = os.path.join(directorio_destino, nombre_archivo)
            
            try:
                shutil.copy2(ruta_origen, ruta_destino)
                exportados += 1
            except Exception as e:
                errores += 1
        
        mensaje = f"Exportación completada:\n{exportados} archivo(s) exportado(s)"
        if errores > 0:
            mensaje += f"\n{errores} error(es)"
        
        QMessageBox.information(self, "Exportación", mensaje)
    
    def exportar_todos_zip(self):
        codigos = self.db_manager.obtener_todos_codigos()
        
        if not codigos:
            QMessageBox.warning(self, "Advertencia", 
                              "No hay códigos para exportar")
            return
        
        ruta_zip, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo ZIP", 
            f"codigos_barras_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            "Archivos ZIP (*.zip);;Todos los archivos (*)"
        )
        
        if not ruta_zip:
            return
        
        try:
            with zipfile.ZipFile(ruta_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                agregados = 0
                errores = 0
                
                for codigo in codigos:
                    if len(codigo) == 8:
                        id_db, codigo_barras, id_unico, fecha, nombre_empleado, descripcion, formato, nombre_archivo_db = codigo
                    else:
                        id_db, codigo_barras, id_unico, fecha, nombre_empleado, descripcion, formato = codigo
                        nombre_empleado_limpio = self.limpiar_nombre_archivo(nombre_empleado or "sin_nombre")
                        nombre_archivo_db = f"{nombre_empleado_limpio}_{codigo_barras}.png"
                    
                    ruta_imagen = f"codigos_generados/{nombre_archivo_db}"
                    
                    if os.path.exists(ruta_imagen):
                        zipf.write(ruta_imagen, nombre_archivo_db)
                        agregados += 1
                    else:
                        errores += 1
            
            mensaje = f"ZIP creado exitosamente:\n{agregados} archivo(s) incluido(s)"
            if errores > 0:
                mensaje += f"\n{errores} archivo(s) no encontrado(s)"
            
            QMessageBox.information(self, "Éxito", mensaje)
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Error al crear el archivo ZIP:\n{str(e)}")
    
    def backup_base_datos(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_backup = f"codigos_barras_backup_{timestamp}.db"
        
        ruta_backup, _ = QFileDialog.getSaveFileName(
            self, "Guardar Backup", 
            nombre_backup,
            "Archivos de Base de Datos (*.db);;Todos los archivos (*)"
        )
        
        if not ruta_backup:
            return
        
        try:
            shutil.copy2("codigos_barras.db", ruta_backup)
            QMessageBox.information(self, "Éxito", 
                                  f"Backup creado exitosamente:\n{ruta_backup}")
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Error al crear el backup:\n{str(e)}")
    
    def mostrar_detalle_codigo(self):
        self.ver_imagen_codigo()
    
    def eliminar_codigo(self):
        resultado = self.obtener_fila_seleccionada()
        if resultado is None:
            QMessageBox.warning(self, "Advertencia", 
                              "Por favor seleccione un código de la tabla")
            return
        
        id_db, codigo_barras, id_unico, formato, nombre_archivo = resultado
        
        respuesta = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar este código?\n"
            f"ID Único: {id_unico}\n\n"
            "Nota: La imagen no se eliminará del disco.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            if self.db_manager.eliminar_codigo(id_db):
                QMessageBox.information(self, "Éxito", 
                                      "Código eliminado de la base de datos")
                self.cargar_codigos_existentes()
                self.actualizar_estadisticas()
            else:
                QMessageBox.warning(self, "Error", 
                                  "No se pudo eliminar el código")
    
    def limpiar_base_datos(self):
        respuesta = QMessageBox.question(
            self, "Confirmar Limpieza",
            "¿Está seguro de que desea eliminar TODOS los códigos de la base de datos?\n\n"
            "Esta acción NO se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            if self.db_manager.limpiar_base_datos():
                QMessageBox.information(self, "Éxito", 
                                      "Base de datos limpiada exitosamente")
                self.cargar_codigos_existentes()
                self.actualizar_estadisticas()
                self.actualizar_id_preview()
            else:
                QMessageBox.warning(self, "Error", 
                                  "No se pudo limpiar la base de datos")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    ventana = VentanaPrincipal()
    ventana.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

