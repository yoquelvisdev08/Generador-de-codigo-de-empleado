"""
Controlador principal - Coordina la lógica de presentación
"""
import os
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QMessageBox, QFileDialog

from config.settings import IMAGES_DIR
from src.models.database import DatabaseManager
from src.models.barcode_model import BarcodeModel
from src.services.barcode_service import BarcodeService
from src.services.export_service import ExportService
from src.views.main_window import MainWindow
from src.utils.file_utils import obtener_ruta_imagen
from src.utils.auth_utils import solicitar_password
from src.utils.id_generator import IDGenerator


class MainController:
    """Controlador principal que coordina modelos, servicios y vistas"""
    
    def __init__(self):
        """Inicializa el controlador y sus dependencias"""
        self.db_manager = DatabaseManager()
        self.barcode_service = BarcodeService()
        self.export_service = ExportService()
        
        # Configurar formatos disponibles en el panel de generación
        formatos = self.barcode_service.obtener_formatos_disponibles()
        self.main_window = MainWindow(formatos_disponibles=formatos)
        
        self._conectar_senales()
        self._cargar_datos_iniciales()
    
    def _conectar_senales(self):
        """Conecta las señales de los widgets con los métodos del controlador"""
        # Panel de generación
        self.main_window.generation_panel.boton_generar.clicked.connect(self.generar_codigo)
        # Conectar señales para actualización en tiempo real del ID
        self.main_window.generation_panel.conectar_senales_actualizacion(self.actualizar_id_preview)
        
        # Panel de listado
        self.main_window.list_panel.campo_busqueda.textChanged.connect(self.buscar_codigos)
        self.main_window.list_panel.boton_refrescar.clicked.connect(self.cargar_codigos)
        self.main_window.list_panel.tabla_codigos.doubleClicked.connect(self.mostrar_detalle_codigo)
        self.main_window.list_panel.boton_ver_imagen.clicked.connect(self.ver_imagen_codigo)
        self.main_window.list_panel.boton_exportar.clicked.connect(self.exportar_seleccionados)
        self.main_window.list_panel.boton_exportar_todos.clicked.connect(self.exportar_todos_zip)
        self.main_window.list_panel.boton_backup.clicked.connect(self.backup_base_datos)
        self.main_window.list_panel.boton_eliminar.clicked.connect(self.eliminar_codigo)
        self.main_window.list_panel.boton_limpiar.clicked.connect(self.limpiar_base_datos)
    
    def _cargar_datos_iniciales(self):
        """Carga los datos iniciales en la interfaz"""
        self.cargar_codigos()
        self.actualizar_id_preview()
        self.actualizar_estadisticas()
    
    def generar_codigo(self):
        """Genera un nuevo código de barras"""
        datos = self.main_window.generation_panel.obtener_datos()
        nombre_empleado = datos['nombre_empleado']
        formato = datos['formato']
        descripcion = datos['descripcion']
        opciones_id = self.main_window.generation_panel.obtener_opciones_id()
        
        if not nombre_empleado:
            QMessageBox.warning(
                self.main_window, "Advertencia",
                "Por favor ingrese el nombre del empleado"
            )
            return
        
        try:
            # Generar ID personalizado según las opciones seleccionadas
            id_unico_generado = IDGenerator.generar_id_personalizado(
                tipo=opciones_id['tipo_caracteres'],
                longitud=opciones_id['cantidad_caracteres'],
                incluir_nombre=opciones_id['incluir_nombre'],
                nombre_empleado=nombre_empleado if opciones_id['incluir_nombre'] else None,
                verificar_duplicado=self.db_manager.verificar_codigo_existe
            )
            
            codigo_barras, id_unico_archivo, ruta_imagen = self.barcode_service.generar_codigo_barras(
                id_unico_generado, formato, id_unico_generado, nombre_empleado
            )
            
            valido, mensaje_error = self.barcode_service.validar_codigo_barras(
                ruta_imagen, id_unico_generado
            )
            
            if not valido:
                if ruta_imagen.exists():
                    ruta_imagen.unlink()
                QMessageBox.critical(
                    self.main_window, "Error de Validación",
                    f"El código de barras generado no es válido:\n{mensaje_error}\n\n"
                    f"El código no se ha guardado. Por favor intente generar nuevamente."
                )
                return
            
            nombre_archivo = ruta_imagen.name
            
            exito = self.db_manager.insertar_codigo(
                codigo_barras, id_unico_generado, formato, nombre_empleado, descripcion, nombre_archivo
            )
            
            if not exito:
                if ruta_imagen.exists():
                    ruta_imagen.unlink()
                QMessageBox.warning(
                    self.main_window, "Error",
                    "No se pudo guardar el código en la base de datos.\n"
                    "Puede que el ID único ya exista."
                )
                return
            
            self.main_window.generation_panel.mostrar_vista_previa(str(ruta_imagen))
            self.cargar_codigos()
            self.actualizar_estadisticas()
            self.actualizar_id_preview()
            self.main_window.generation_panel.limpiar_formulario()
            
            QMessageBox.information(
                self.main_window, "Éxito",
                f"Código de barras generado y validado exitosamente.\n"
                f"ID Único: {id_unico_generado}\n"
                f"Empleado: {nombre_empleado}\n"
                f"Validación: El código escaneado coincide con el ID generado"
            )
        except Exception as e:
            QMessageBox.critical(
                self.main_window, "Error",
                f"Error al generar el código de barras:\n{str(e)}"
            )
    
    def cargar_codigos(self):
        """Carga todos los códigos en la tabla"""
        termino = self.main_window.list_panel.obtener_termino_busqueda()
        
        if termino:
            codigos = self.db_manager.buscar_codigo(termino)
        else:
            codigos = self.db_manager.obtener_todos_codigos()
        
        self.main_window.list_panel.cargar_codigos(codigos)
    
    def buscar_codigos(self):
        """Busca códigos según el término de búsqueda"""
        self.cargar_codigos()
    
    def mostrar_detalle_codigo(self):
        """Muestra el detalle del código seleccionado"""
        self.ver_imagen_codigo()
    
    def ver_imagen_codigo(self):
        """Muestra la imagen del código seleccionado"""
        resultado = self.main_window.list_panel.obtener_fila_seleccionada()
        if resultado is None:
            QMessageBox.warning(
                self.main_window, "Advertencia",
                "Por favor seleccione un código de la tabla"
            )
            return
        
        id_db, codigo_barras, id_unico, formato, nombre_archivo = resultado
        ruta_imagen = IMAGES_DIR / nombre_archivo
        
        if not ruta_imagen.exists():
            QMessageBox.warning(
                self.main_window, "Error",
                f"No se encontró la imagen del código de barras.\n"
                f"Ruta buscada: {ruta_imagen}"
            )
            return
        
        self.main_window.generation_panel.mostrar_vista_previa(str(ruta_imagen))
    
    def exportar_seleccionados(self):
        """Exporta los códigos seleccionados"""
        filas = self.main_window.list_panel.obtener_filas_seleccionadas()
        
        if not filas:
            QMessageBox.warning(
                self.main_window, "Advertencia",
                "Por favor seleccione al menos un código de la tabla"
            )
            return
        
        directorio_destino = QFileDialog.getExistingDirectory(
            self.main_window, "Seleccionar carpeta para exportar"
        )
        
        if not directorio_destino:
            return
        
        exportados, errores = self.export_service.exportar_seleccionados(
            filas, Path(directorio_destino)
        )
        
        mensaje = f"Exportación completada:\n{exportados} archivo(s) exportado(s)"
        if errores > 0:
            mensaje += f"\n{errores} error(es)"
        
        QMessageBox.information(self.main_window, "Exportación", mensaje)
    
    def exportar_todos_zip(self):
        """Exporta todos los códigos a un archivo ZIP"""
        codigos = self.db_manager.obtener_todos_codigos()
        
        if not codigos:
            QMessageBox.warning(
                self.main_window, "Advertencia",
                "No hay códigos para exportar"
            )
            return
        
        nombre_zip = self.export_service.generar_nombre_zip()
        ruta_zip, _ = QFileDialog.getSaveFileName(
            self.main_window, "Guardar archivo ZIP",
            nombre_zip,
            "Archivos ZIP (*.zip);;Todos los archivos (*)"
        )
        
        if not ruta_zip:
            return
        
        agregados, errores = self.export_service.exportar_todos_zip(
            codigos, Path(ruta_zip)
        )
        
        mensaje = f"ZIP creado exitosamente:\n{agregados} archivo(s) incluido(s)"
        if errores > 0:
            mensaje += f"\n{errores} archivo(s) no encontrado(s)"
        
        QMessageBox.information(self.main_window, "Éxito", mensaje)
    
    def backup_base_datos(self):
        """Crea un backup de la base de datos"""
        nombre_backup = self.export_service.generar_nombre_backup()
        ruta_backup, _ = QFileDialog.getSaveFileName(
            self.main_window, "Guardar Backup",
            nombre_backup,
            "Archivos de Base de Datos (*.db);;Todos los archivos (*)"
        )
        
        if not ruta_backup:
            return
        
        if self.export_service.crear_backup_base_datos(Path(ruta_backup)):
            QMessageBox.information(
                self.main_window, "Éxito",
                f"Backup creado exitosamente:\n{ruta_backup}"
            )
        else:
            QMessageBox.critical(
                self.main_window, "Error",
                "Error al crear el backup"
            )
    
    def eliminar_codigo(self):
        """Elimina un código de la base de datos"""
        resultado = self.main_window.list_panel.obtener_fila_seleccionada()
        if resultado is None:
            QMessageBox.warning(
                self.main_window, "Advertencia",
                "Por favor seleccione un código de la tabla"
            )
            return
        
        id_db, codigo_barras, id_unico, formato, nombre_archivo = resultado
        
        # Solicitar contraseña antes de eliminar
        if not solicitar_password(self.main_window, "eliminar este código"):
            return
        
        respuesta = QMessageBox.question(
            self.main_window, "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar este código?\n"
            f"ID Único: {id_unico}\n\n"
            "Nota: La imagen no se eliminará del disco.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            if self.db_manager.eliminar_codigo(id_db):
                QMessageBox.information(
                    self.main_window, "Éxito",
                    "Código eliminado de la base de datos.\n\n"
                    "Nota: Se creó un backup automático antes de la eliminación."
                )
                self.cargar_codigos()
                self.actualizar_estadisticas()
            else:
                QMessageBox.warning(
                    self.main_window, "Error",
                    "No se pudo eliminar el código"
                )
    
    def limpiar_base_datos(self):
        """Limpia toda la base de datos"""
        # Solicitar contraseña antes de limpiar la base de datos
        if not solicitar_password(self.main_window, "limpiar toda la base de datos"):
            return
        
        respuesta = QMessageBox.question(
            self.main_window, "Confirmar Limpieza",
            "¿Está seguro de que desea eliminar TODOS los códigos de la base de datos?\n\n"
            "Esta acción NO se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            if self.db_manager.limpiar_base_datos():
                QMessageBox.information(
                    self.main_window, "Éxito",
                    "Base de datos limpiada exitosamente.\n\n"
                    "Nota: Se creó un backup automático antes de la limpieza."
                )
                self.cargar_codigos()
                self.actualizar_estadisticas()
                self.actualizar_id_preview()
            else:
                QMessageBox.warning(
                    self.main_window, "Error",
                    "No se pudo limpiar la base de datos.\n\n"
                    "Verifique que se haya creado el backup automático."
                )
    
    def actualizar_id_preview(self):
        """Actualiza la vista previa del ID que se generará en tiempo real"""
        try:
            opciones = self.main_window.generation_panel.obtener_opciones_id()
            nombre_empleado = opciones['nombre_empleado']
            incluir_nombre = opciones['incluir_nombre']
            
            # Si se debe incluir el nombre pero no hay nombre, mostrar mensaje
            if incluir_nombre and not nombre_empleado:
                self.main_window.generation_panel.actualizar_id_preview(
                    "Ingrese el nombre del empleado para ver el ID"
                )
                return
            
            # Generar un ID de ejemplo (sin verificar duplicados para la vista previa)
            id_ejemplo = IDGenerator.generar_id_personalizado(
                tipo=opciones['tipo_caracteres'],
                longitud=opciones['cantidad_caracteres'],
                incluir_nombre=incluir_nombre,
                nombre_empleado=nombre_empleado if incluir_nombre else None,
                verificar_duplicado=None  # No verificar en la vista previa
            )
            
            self.main_window.generation_panel.actualizar_id_preview(id_ejemplo)
        except Exception:
            # Si hay error, usar el método tradicional
            siguiente_id = self.db_manager.obtener_siguiente_id_secuencial()
            self.main_window.generation_panel.actualizar_id_preview(siguiente_id)
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas en la barra de estado"""
        estadisticas = self.db_manager.obtener_estadisticas()
        mensaje = (
            f"Total de códigos: {estadisticas['total_codigos']} | "
            f"Formatos: {estadisticas['formatos_diferentes']}"
        )
        self.main_window.actualizar_estadisticas(mensaje)
    
    def show(self):
        """Muestra la ventana principal"""
        self.main_window.show()

