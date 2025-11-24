"""
Controlador para la gestión de códigos de barras de servicio
"""
import logging
import zipfile
from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox, QFileDialog

from config.settings import IMAGES_DIR
from src.models.database import DatabaseManager
from src.services.barcode_service import BarcodeService
from src.services.excel_service import ExcelService
from src.utils.id_generator import IDGenerator
from src.utils.file_utils import obtener_ruta_imagen
from src.utils.auth_utils import solicitar_autenticacion_admin
from src.views.widgets.progress_dialog import ProgressDialog

logger = logging.getLogger(__name__)


class ServiceController:
    """Controlador para gestionar códigos de barras de servicio"""
    
    def __init__(self, service_panel, db_manager: DatabaseManager, usuario: str = "admin", rol: str = "admin"):
        """
        Inicializa el controlador de servicios
        
        Args:
            service_panel: Panel de servicios
            db_manager: Gestor de base de datos
            usuario: Usuario actual (para autenticación)
            rol: Rol del usuario actual
        """
        self.service_panel = service_panel
        self.db_manager = db_manager
        self.barcode_service = BarcodeService()
        self.excel_service = ExcelService(db_manager)
        self.servicio_seleccionado = None
        self.usuario = usuario
        self.rol = rol
        
        self._conectar_senales()
        self._cargar_datos_iniciales()
    
    def _conectar_senales(self):
        """Conecta las señales de los widgets con los métodos del controlador"""
        self.service_panel.boton_generar.clicked.connect(self.generar_codigo_servicio)
        self.service_panel.boton_descargar_individual.clicked.connect(self.descargar_individual_png)
        self.service_panel.boton_descargar_masivo.clicked.connect(self.descargar_masivo_zip)
        self.service_panel.campo_nombre_servicio.textChanged.connect(self.actualizar_id_preview)
        self.service_panel.campo_busqueda.textChanged.connect(self.buscar_servicios)
        self.service_panel.boton_refrescar.clicked.connect(self.cargar_servicios)
        self.service_panel.tabla_servicios.itemSelectionChanged.connect(self.mostrar_imagen_seleccionada)
        self.service_panel.boton_importar_excel.clicked.connect(self.importar_servicios_excel)
        self.service_panel.boton_exportar_excel.clicked.connect(self.exportar_servicios_excel)
        self.service_panel.boton_descargar_ejemplo_excel.clicked.connect(self.descargar_ejemplo_excel)
        self.service_panel.boton_eliminar.clicked.connect(self.eliminar_servicio)
    
    def _cargar_datos_iniciales(self):
        """Carga los datos iniciales en la interfaz"""
        self.actualizar_id_preview()
        self.cargar_servicios()
    
    def cargar_servicios(self):
        """Carga todos los servicios en la tabla"""
        termino = self.service_panel.obtener_termino_busqueda()
        
        if termino:
            servicios = self.db_manager.buscar_servicio(termino)
        else:
            servicios = self.db_manager.obtener_todos_servicios()
        
        self.service_panel.cargar_servicios(servicios)
    
    def buscar_servicios(self):
        """Busca servicios según el término de búsqueda"""
        self.cargar_servicios()
    
    def mostrar_imagen_seleccionada(self):
        """Muestra automáticamente la imagen del servicio seleccionado en la tabla"""
        resultado = self.service_panel.obtener_fila_seleccionada()
        if resultado is None:
            self.service_panel.boton_descargar_individual.setEnabled(False)
            return
        
        id_db, codigo_barras, id_unico, nombre_servicio, formato = resultado
        
        # Obtener el servicio completo de la base de datos para obtener nombre_archivo
        servicio_completo = self.db_manager.obtener_servicio_por_id(id_db)
        if not servicio_completo:
            self.service_panel.label_vista_previa.setText("Servicio no encontrado")
            self.service_panel.boton_descargar_individual.setEnabled(False)
            return
        
        nombre_archivo = servicio_completo[6] if len(servicio_completo) > 6 else None
        
        if nombre_archivo:
            from config.settings import IMAGES_DIR
            ruta_imagen = IMAGES_DIR / nombre_archivo
            
            if ruta_imagen.exists():
                informacion_imagen = self.barcode_service.obtener_informacion_imagen(ruta_imagen)
                self.service_panel.mostrar_vista_previa(str(ruta_imagen), informacion_imagen)
                
                # Actualizar servicio seleccionado
                self.servicio_seleccionado = {
                    'id': id_db,
                    'codigo_barras': codigo_barras,
                    'id_unico': id_unico,
                    'nombre_servicio': nombre_servicio,
                    'nombre_archivo': nombre_archivo
                }
                self.service_panel.boton_descargar_individual.setEnabled(True)
            else:
                self.service_panel.label_vista_previa.setText(
                    f"Imagen no encontrada:\n{nombre_archivo}"
                )
                self.service_panel.boton_descargar_individual.setEnabled(False)
        else:
            self.service_panel.label_vista_previa.setText("Servicio sin imagen")
            self.service_panel.boton_descargar_individual.setEnabled(False)
    
    def actualizar_id_preview(self):
        """Actualiza la vista previa del ID que se generará"""
        try:
            siguiente_id = self.db_manager.obtener_siguiente_id_secuencial()
            self.service_panel.actualizar_id_preview(siguiente_id)
        except Exception as e:
            logger.error(f"Error al actualizar vista previa de ID: {e}")
            self.service_panel.actualizar_id_preview("Error al generar ID")
    
    def generar_codigo_servicio(self):
        """Genera un nuevo código de barras de servicio"""
        nombre_servicio = self.service_panel.obtener_nombre_servicio()
        
        if not nombre_servicio:
            QMessageBox.warning(
                self.service_panel, "Advertencia",
                "Por favor ingrese el nombre del servicio"
            )
            return
        
        try:
            formato = "Code128"
            tamano_fuente = self.service_panel.obtener_tamano_fuente()
            
            id_unico_generado = IDGenerator.generar_id_personalizado(
                tipo="alfanumerico",
                longitud=10,
                incluir_nombre=False,
                texto_personalizado=None,
                verificar_duplicado=self.db_manager.verificar_servicio_existe
            )
            
            codigo_barras, id_unico_archivo, ruta_imagen = self.barcode_service.generar_codigo_barras(
                id_unico_generado, formato, id_unico_generado, None, None, 
                texto_debajo=nombre_servicio, tamano_fuente_texto=tamano_fuente
            )
            
            valido, mensaje_error = self.barcode_service.validar_codigo_barras(
                ruta_imagen, id_unico_generado
            )
            
            if not valido:
                if ruta_imagen.exists():
                    ruta_imagen.unlink()
                QMessageBox.critical(
                    self.service_panel, "Error de Validación",
                    f"El código de barras generado no es válido:\n{mensaje_error}\n\n"
                    f"El código no se ha guardado. Por favor intente generar nuevamente."
                )
                return
            
            informacion_imagen = self.barcode_service.obtener_informacion_imagen(ruta_imagen)
            
            nombre_archivo = ruta_imagen.name
            
            servicio_id = self.db_manager.insertar_servicio(
                codigo_barras, id_unico_generado, nombre_servicio, formato, nombre_archivo
            )
            
            if servicio_id is None:
                if ruta_imagen.exists():
                    ruta_imagen.unlink()
                QMessageBox.warning(
                    self.service_panel, "Error",
                    "No se pudo guardar el código en la base de datos.\n"
                    "Puede que el ID único ya exista."
                )
                return
            
            self.servicio_seleccionado = {
                'id': servicio_id,
                'codigo_barras': codigo_barras,
                'id_unico': id_unico_generado,
                'nombre_servicio': nombre_servicio,
                'nombre_archivo': nombre_archivo
            }
            
            self.service_panel.mostrar_vista_previa(
                str(ruta_imagen),
                informacion_imagen
            )
            self.actualizar_id_preview()
            self.service_panel.limpiar_formulario()
            self.cargar_servicios()  # Refrescar tabla
            
            mensaje_exito = (
                f"Código de barras de servicio generado exitosamente.\n\n"
                f"ID Único: {id_unico_generado}\n"
                f"Servicio: {nombre_servicio}\n"
                f"Validación: El código escaneado coincide con el ID generado"
            )
            
            if informacion_imagen:
                if 'dimensiones' in informacion_imagen:
                    dims = informacion_imagen['dimensiones']
                    mensaje_exito += (
                        f"\n\nInformación de la imagen:\n"
                        f"Dimensiones: {dims.get('ancho', 'N/A')} x {dims.get('alto', 'N/A')} píxeles"
                    )
                if 'tamano_archivo_kb' in informacion_imagen:
                    mensaje_exito += f"\nTamaño: {informacion_imagen['tamano_archivo_kb']} KB"
            
            QMessageBox.information(
                self.service_panel, "Éxito",
                mensaje_exito
            )
        except Exception as e:
            logger.error(f"Error al generar código de servicio: {e}", exc_info=True)
            QMessageBox.critical(
                self.service_panel, "Error",
                f"Error al generar el código de barras:\n{str(e)}"
            )
    
    def descargar_individual_png(self):
        """Descarga un servicio individual en formato PNG con verificación OCR"""
        if not self.servicio_seleccionado:
            QMessageBox.warning(
                self.service_panel, "Advertencia",
                "Por favor genere un código de barras primero"
            )
            return
        
        try:
            servicio = self.servicio_seleccionado
            nombre_archivo = servicio['nombre_archivo']
            ruta_imagen = IMAGES_DIR / nombre_archivo
            
            if not ruta_imagen.exists():
                QMessageBox.warning(
                    self.service_panel, "Error",
                    f"La imagen del servicio no se encuentra: {nombre_archivo}"
                )
                return
            
            nombre_servicio_limpio = servicio['nombre_servicio'].replace(" ", "_")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_descarga = f"servicio_{nombre_servicio_limpio}_{servicio['id_unico']}_{timestamp}.png"
            
            ruta_destino, _ = QFileDialog.getSaveFileName(
                self.service_panel,
                "Guardar Código de Barras de Servicio",
                nombre_descarga,
                "Archivos PNG (*.png);;Todos los archivos (*)"
            )
            
            if not ruta_destino:
                return
            
            ruta_destino_path = Path(ruta_destino)
            
            import shutil
            shutil.copy2(ruta_imagen, ruta_destino_path)
            
            codigo_esperado = servicio['codigo_barras']
            valido, mensaje_validacion = self.barcode_service.validar_codigo_barras(
                ruta_destino_path,
                codigo_esperado
            )
            
            if not valido:
                QMessageBox.warning(
                    self.service_panel, "Advertencia de Verificación",
                    f"El código de barras se descargó correctamente, pero la verificación falló:\n{mensaje_validacion}\n\n"
                    f"El archivo se guardó en: {ruta_destino_path}"
                )
            else:
                QMessageBox.information(
                    self.service_panel, "Éxito",
                    f"Código de barras descargado y verificado correctamente.\n\n"
                    f"Archivo guardado en: {ruta_destino_path}\n"
                    f"Verificación: El código de barras leído coincide con el de la tabla"
                )
        except Exception as e:
            logger.error(f"Error al descargar servicio individual: {e}", exc_info=True)
            QMessageBox.critical(
                self.service_panel, "Error",
                f"Error al descargar el código de barras:\n{str(e)}"
            )
    
    def descargar_masivo_zip(self):
        """Descarga todos los servicios en un archivo ZIP con verificación OCR"""
        servicios = self.db_manager.obtener_todos_servicios()
        
        if not servicios:
            QMessageBox.warning(
                self.service_panel, "Advertencia",
                "No hay servicios para descargar"
            )
            return
        
        nombre_zip = f"servicios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        ruta_zip, _ = QFileDialog.getSaveFileName(
            self.service_panel,
            "Guardar Servicios en ZIP",
            nombre_zip,
            "Archivos ZIP (*.zip);;Todos los archivos (*)"
        )
        
        if not ruta_zip:
            return
        
        ruta_zip_path = Path(ruta_zip)
        
        progress = ProgressDialog("Generando archivo ZIP de servicios...", self.service_panel)
        progress.set_cancelable(True)
        progress.show()
        
        try:
            archivos_generados = []
            errores = []
            servicios_verificados = 0
            servicios_fallidos = 0
            
            with zipfile.ZipFile(ruta_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                total = len(servicios)
                
                for indice, servicio in enumerate(servicios, 1):
                    if progress.fue_cancelado():
                        break
                    
                    progress.actualizar_progreso(
                        indice,
                        total,
                        f"Procesando servicio {indice} de {total}: {servicio[3]}"
                    )
                    
                    try:
                        servicio_id = servicio[0]
                        codigo_barras = servicio[1]
                        id_unico = servicio[2]
                        nombre_servicio = servicio[3]
                        nombre_archivo = servicio[6] if len(servicio) > 6 else None
                        
                        if not nombre_archivo:
                            errores.append(f"Servicio {nombre_servicio}: Sin archivo de imagen")
                            continue
                        
                        ruta_imagen = IMAGES_DIR / nombre_archivo
                        
                        if not ruta_imagen.exists():
                            errores.append(f"Servicio {nombre_servicio}: Imagen no encontrada")
                            continue
                        
                        nombre_servicio_limpio = nombre_servicio.replace(" ", "_")
                        nombre_en_zip = f"{nombre_servicio_limpio}_{id_unico}.png"
                        
                        zipf.write(ruta_imagen, nombre_en_zip)
                        
                        valido, mensaje_validacion = self.barcode_service.validar_codigo_barras(
                            ruta_imagen,
                            codigo_barras
                        )
                        
                        if valido:
                            servicios_verificados += 1
                        else:
                            servicios_fallidos += 1
                            logger.warning(f"Verificación falló para servicio {nombre_servicio}: {mensaje_validacion}")
                        
                        archivos_generados.append(nombre_en_zip)
                    except Exception as e:
                        logger.error(f"Error al procesar servicio {servicio[3]}: {e}")
                        errores.append(f"Servicio {servicio[3]}: {str(e)}")
            
            progress.marcar_completado()
            progress.close()
            
            if progress.fue_cancelado():
                if ruta_zip_path.exists():
                    ruta_zip_path.unlink()
                QMessageBox.information(
                    self.service_panel, "Cancelado",
                    "La descarga masiva fue cancelada."
                )
                return
            
            mensaje = (
                f"ZIP creado exitosamente:\n"
                f"✓ Servicios incluidos: {len(archivos_generados)}\n"
                f"✓ Verificados correctamente: {servicios_verificados}\n"
                f"⚠ Fallos de verificación: {servicios_fallidos}"
            )
            
            if errores:
                mensaje += f"\n\nErrores: {len(errores)}"
                if len(errores) <= 10:
                    mensaje += "\n" + "\n".join(errores)
                else:
                    mensaje += "\n" + "\n".join(errores[:10]) + f"\n... y {len(errores) - 10} errores más"
            
            QMessageBox.information(
                self.service_panel, "Éxito",
                f"{mensaje}\n\nArchivo guardado en: {ruta_zip_path}"
            )
        except Exception as e:
            progress.close()
            logger.error(f"Error al generar ZIP de servicios: {e}", exc_info=True)
            QMessageBox.critical(
                self.service_panel, "Error",
                f"Error al generar el archivo ZIP:\n{str(e)}"
            )
    
    def exportar_servicios_excel(self):
        """Exporta todos los servicios a un archivo Excel"""
        try:
            servicios = self.db_manager.obtener_todos_servicios()
            
            if not servicios:
                QMessageBox.warning(
                    self.service_panel, "Advertencia",
                    "No hay servicios para exportar"
                )
                return
            
            # Solicitar ruta donde guardar
            ruta_archivo, _ = QFileDialog.getSaveFileName(
                self.service_panel,
                "Exportar Servicios a Excel",
                f"servicios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Archivos Excel (*.xlsx)"
            )
            
            if not ruta_archivo:
                return
            
            ruta_path = Path(ruta_archivo)
            
            # Exportar servicios
            exito, mensaje = self.excel_service.exportar_servicios_a_excel(ruta_path)
            
            if exito:
                QMessageBox.information(
                    self.service_panel,
                    "Exportación Exitosa",
                    f"{mensaje}\n\nArchivo guardado en:\n{ruta_path}"
                )
            else:
                QMessageBox.warning(
                    self.service_panel,
                    "Error al Exportar",
                    mensaje
                )
        except Exception as e:
            logger.error(f"Error al exportar servicios a Excel: {e}", exc_info=True)
            QMessageBox.critical(
                self.service_panel, "Error",
                f"Error inesperado al exportar: {str(e)}"
            )
    
    def eliminar_servicio(self):
        """Elimina uno o varios servicios de la base de datos"""
        servicios_seleccionados = self.service_panel.obtener_filas_seleccionadas()
        if not servicios_seleccionados:
            QMessageBox.warning(
                self.service_panel, "Advertencia",
                "Por favor seleccione al menos un servicio de la tabla"
            )
            return
        
        cantidad = len(servicios_seleccionados)
        
        # Verificar autenticación de administrador antes de eliminar
        accion = f"eliminar {cantidad} servicio(s)" if cantidad > 1 else "eliminar este servicio"
        if not solicitar_autenticacion_admin(
            self.service_panel, 
            accion,
            self.usuario,
            self.rol
        ):
            return
        
        # Preparar mensaje de confirmación
        if cantidad == 1:
            id_db, codigo_barras, id_unico, nombre_servicio, formato = servicios_seleccionados[0]
            mensaje_confirmacion = (
                f"¿Está seguro de que desea eliminar este servicio?\n"
                f"Nombre: {nombre_servicio}\n"
                f"ID Único: {id_unico}\n\n"
                "Nota: La imagen también se eliminará del disco."
            )
        else:
            nombres = [s[3] for s in servicios_seleccionados[:5]]  # Primeros 5 nombres
            mensaje_nombres = "\n".join(f"- {nombre}" for nombre in nombres)
            if cantidad > 5:
                mensaje_nombres += f"\n... y {cantidad - 5} servicio(s) más"
            mensaje_confirmacion = (
                f"¿Está seguro de que desea eliminar {cantidad} servicio(s)?\n\n"
                f"Servicios seleccionados:\n{mensaje_nombres}\n\n"
                "Nota: Las imágenes también se eliminarán del disco."
            )
        
        respuesta = QMessageBox.question(
            self.service_panel, "Confirmar Eliminación",
            mensaje_confirmacion,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            eliminados = 0
            errores = []
            
            for id_db, codigo_barras, id_unico, nombre_servicio, formato in servicios_seleccionados:
                if self.db_manager.eliminar_servicio(id_db, eliminar_imagen=True):
                    eliminados += 1
                else:
                    errores.append(f"{nombre_servicio} (ID: {id_db})")
            
            # Mostrar resultado
            if eliminados == cantidad:
                mensaje_exito = (
                    f"{eliminados} servicio(s) eliminado(s) correctamente.\n\n"
                    "Nota: Se creó un backup automático antes de la eliminación."
                )
                QMessageBox.information(
                    self.service_panel, "Éxito",
                    mensaje_exito
                )
            elif eliminados > 0:
                mensaje_parcial = (
                    f"Se eliminaron {eliminados} de {cantidad} servicio(s).\n\n"
                )
                if errores:
                    mensaje_parcial += f"No se pudieron eliminar:\n" + "\n".join(errores[:10])
                    if len(errores) > 10:
                        mensaje_parcial += f"\n... y {len(errores) - 10} más"
                QMessageBox.warning(
                    self.service_panel, "Eliminación Parcial",
                    mensaje_parcial
                )
            else:
                QMessageBox.warning(
                    self.service_panel, "Error",
                    "No se pudo eliminar ningún servicio"
                )
            
            # Refrescar lista y limpiar selección
            self.cargar_servicios()
            self.servicio_seleccionado = None
            self.service_panel.label_vista_previa.setText("La vista previa aparecerá aquí")
            self.service_panel.boton_descargar_individual.setEnabled(False)
    
    def importar_servicios_excel(self):
        """Importa servicios desde un archivo Excel y genera códigos de barras"""
        try:
            # Solicitar archivo a importar
            ruta_archivo, _ = QFileDialog.getOpenFileName(
                self.service_panel,
                "Importar Servicios desde Excel",
                "",
                "Archivos Excel (*.xlsx *.xls)"
            )
            
            if not ruta_archivo:
                return
            
            ruta_path = Path(ruta_archivo)
            
            # Crear diálogo de progreso
            progress_dialog = ProgressDialog("Importando Servicios desde Excel", self.service_panel)
            progress_dialog.set_cancelable(True)
            progress_dialog.show()
            
            # Función callback para actualizar progreso
            def actualizar_progreso(actual, total, mensaje):
                if progress_dialog.fue_cancelado():
                    return
                progress_dialog.actualizar_progreso(actual, total, mensaje)
            
            # Obtener tamaño de fuente del panel
            tamano_fuente = self.service_panel.obtener_tamano_fuente()
            
            # Importar servicios
            exito, estadisticas, errores = self.excel_service.importar_servicios_desde_excel(
                ruta_path,
                callback_progreso=actualizar_progreso,
                tamano_fuente=tamano_fuente
            )
            
            progress_dialog.marcar_completado()
            progress_dialog.close()
            
            if not exito:
                QMessageBox.warning(
                    self.service_panel,
                    "Error al Importar",
                    "\n".join(errores) if errores else "Error desconocido"
                )
                return
            
            # Mostrar resumen
            mensaje = (
                f"Importación completada:\n\n"
                f"Total de filas: {estadisticas['total']}\n"
                f"Servicios generados: {estadisticas['exitosos']}\n"
                f"Duplicados: {estadisticas['duplicados']}\n"
                f"Errores: {estadisticas['errores']}"
            )
            
            if errores and len(errores) <= 10:
                mensaje += f"\n\nErrores:\n" + "\n".join(errores)
            elif errores:
                mensaje += f"\n\nErrores (mostrando primeros 10):\n" + "\n".join(errores[:10]) + f"\n... y {len(errores) - 10} errores más"
            
            QMessageBox.information(
                self.service_panel,
                "Importación Completada",
                mensaje
            )
            
            # Refrescar lista
            self.cargar_servicios()
            
        except Exception as e:
            logger.error(f"Error al importar servicios desde Excel: {e}", exc_info=True)
            QMessageBox.critical(
                self.service_panel, "Error",
                f"Error inesperado al importar: {str(e)}"
            )
    
    def descargar_ejemplo_excel(self):
        """Genera y descarga un archivo Excel de ejemplo para servicios"""
        try:
            # Solicitar ruta donde guardar
            ruta_archivo, _ = QFileDialog.getSaveFileName(
                self.service_panel,
                "Guardar Excel de Ejemplo",
                f"ejemplo_servicios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Archivos Excel (*.xlsx)"
            )
            
            if not ruta_archivo:
                return
            
            ruta_path = Path(ruta_archivo)
            
            # Generar archivo de ejemplo
            exito, mensaje = self.excel_service.generar_excel_ejemplo_servicios(ruta_path)
            
            if exito:
                QMessageBox.information(
                    self.service_panel,
                    "Archivo Generado",
                    f"{mensaje}\n\nArchivo guardado en:\n{ruta_path}"
                )
            else:
                QMessageBox.warning(
                    self.service_panel,
                    "Error",
                    mensaje
                )
        except Exception as e:
            logger.error(f"Error al generar Excel de ejemplo: {e}", exc_info=True)
            QMessageBox.critical(
                self.service_panel, "Error",
                f"Error inesperado: {str(e)}"
            )

