"""
Controlador para el editor de carnet
"""
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QMessageBox, QApplication, QFileDialog
from PyQt6.QtCore import Qt
from PIL import Image

from src.models.database import DatabaseManager
from src.services.carnet_designer import CarnetDesigner
from src.services.html_renderer import HTMLRenderer
from src.models.carnet_template import CarnetTemplate
from config.settings import IMAGES_DIR, CARNETS_DIR
from src.views.widgets.carnet_preview_panel import CarnetPreviewPanel
from src.views.widgets.carnet_controls_panel import CarnetControlsPanel
from src.views.widgets.carnet_employees_panel import CarnetEmployeesPanel


class CarnetController:
    """Controlador para el editor de carnet"""
    
    def __init__(
        self,
        preview_panel: CarnetPreviewPanel,
        controls_panel: CarnetControlsPanel,
        employees_panel: CarnetEmployeesPanel
    ):
        """
        Inicializa el controlador
        
        Args:
            preview_panel: Panel de vista previa
            controls_panel: Panel de controles
            employees_panel: Panel de empleados
        """
        self.preview_panel = preview_panel
        self.controls_panel = controls_panel
        self.employees_panel = employees_panel
        
        self.db_manager = DatabaseManager()
        self.designer = CarnetDesigner()
        self.html_renderer = HTMLRenderer()
        
        self.empleado_actual = None
        self._conectar_senales()
        self._cargar_empleados()
        # Establecer callback para actualización cuando cambien variables
        self.controls_panel.establecer_callback_actualizacion(self.actualizar_vista_previa)
        # Actualizar vista previa inicial después de un breve delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self.actualizar_vista_previa)
    
    def _conectar_senales(self):
        """Conecta las señales de los widgets"""
        # Controles que actualizan la vista previa
        self.controls_panel.spin_logo_x.valueChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.spin_logo_y.valueChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.spin_logo_ancho.valueChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.spin_logo_alto.valueChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.spin_opacidad.valueChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.spin_nombre_x.valueChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.spin_nombre_y.valueChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.spin_nombre_tamaño.valueChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.spin_codigo_x.valueChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.spin_codigo_y.valueChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.spin_codigo_ancho.valueChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.spin_codigo_alto.valueChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.check_mostrar_nombre.toggled.connect(self.actualizar_vista_previa)
        self.controls_panel.check_mostrar_numero.toggled.connect(self.actualizar_vista_previa)
        self.controls_panel.check_mostrar_empresa.toggled.connect(self.actualizar_vista_previa)
        self.controls_panel.check_mostrar_web.toggled.connect(self.actualizar_vista_previa)
        self.controls_panel.campo_empresa.textChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.campo_web.textChanged.connect(self.actualizar_vista_previa)
        self.controls_panel.boton_cargar_logo.clicked.connect(self.actualizar_vista_previa)
        self.controls_panel.boton_imagen_fondo.clicked.connect(self.actualizar_vista_previa)
        self.controls_panel.boton_color_fondo.clicked.connect(self.actualizar_vista_previa)
        self.controls_panel.boton_color_nombre.clicked.connect(self.actualizar_vista_previa)
        self.controls_panel.boton_cargar_html.clicked.connect(self.actualizar_vista_previa)
        
        # Acciones del panel de empleados
        self.employees_panel.tabla_empleados.itemSelectionChanged.connect(self.seleccionar_empleado)
        self.employees_panel.boton_vista_previa.clicked.connect(self.mostrar_vista_previa_empleado)
        self.employees_panel.boton_generar_individual.clicked.connect(self.generar_carnet_individual)
        self.employees_panel.boton_generar_masivo.clicked.connect(self.generar_carnets_masivos)
        self.employees_panel.boton_generar_individual_pdf.clicked.connect(self.generar_carnet_individual_pdf)
        self.employees_panel.boton_generar_masivo_pdf.clicked.connect(self.generar_carnets_masivos_pdf)
        self.employees_panel.campo_busqueda.textChanged.connect(self.buscar_empleados)
    
    def _cargar_empleados(self):
        """Carga los empleados desde la base de datos"""
        empleados = self.db_manager.obtener_todos_codigos()
        self.employees_panel.cargar_empleados(empleados)
    
    def refrescar_empleados(self):
        """Refresca la lista de empleados desde la base de datos"""
        self._cargar_empleados()
    
    def buscar_empleados(self):
        """Busca empleados según el término de búsqueda"""
        termino = self.employees_panel.obtener_termino_busqueda()
        
        if termino:
            empleados = self.db_manager.buscar_codigo(termino)
        else:
            empleados = self.db_manager.obtener_todos_codigos()
        
        self.employees_panel.cargar_empleados(empleados)
    
    def seleccionar_empleado(self):
        """Se ejecuta cuando se selecciona un empleado"""
        empleado = self.employees_panel.obtener_empleado_seleccionado()
        if empleado:
            self.empleado_actual = empleado
            # Actualizar variables en el panel de controles con datos del empleado
            self._actualizar_variables_desde_empleado(empleado)
            self.actualizar_vista_previa()
    
    def _actualizar_variables_desde_empleado(self, empleado):
        """Actualiza las variables del panel con datos del empleado seleccionado"""
        if not empleado:
            return
        
        # Desempaquetar: puede ser varios formatos
        if len(empleado) >= 7:
            id_db, codigo_barras, id_unico, nombre_empleado, descripcion, formato, nombre_archivo = empleado
        elif len(empleado) >= 6:
            id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = empleado
            descripcion = ""
        else:
            return
        
        codigo_path = IMAGES_DIR / nombre_archivo
        
        # Actualizar campos de variables dinámicamente
        if nombre_empleado and "nombre" in self.controls_panel.campos_variables:
            campo_nombre = self.controls_panel.campos_variables["nombre"]
            if not isinstance(campo_nombre, dict):
                campo_nombre.setText(nombre_empleado)
        
        # Actualizar ID único (automático)
        if "id_unico" in self.controls_panel.campos_variables:
            campo_id = self.controls_panel.campos_variables["id_unico"]
            if not isinstance(campo_id, dict):
                campo_id.setText(id_unico or "")
        
        # Actualizar código de barras (automático)
        if "codigo_barras" in self.controls_panel.campos_variables:
            campo_codigo = self.controls_panel.campos_variables["codigo_barras"]
            if isinstance(campo_codigo, dict) and "campo" in campo_codigo:
                if codigo_path.exists():
                    campo_codigo["campo"].setText(str(codigo_path))
                else:
                    campo_codigo["campo"].setText("No disponible")
    
    def actualizar_vista_previa(self):
        """Actualiza la vista previa del carnet"""
        # Verificar si se está usando template HTML
        if self.controls_panel.usar_template_html():
            self._actualizar_vista_previa_html()
        else:
            self._actualizar_vista_previa_pil()
    
    def _actualizar_vista_previa_html(self):
        """Actualiza la vista previa usando template HTML"""
        import logging
        logger = logging.getLogger(__name__)
        
        html_template = self.controls_panel.obtener_html_template()
        if not html_template:
            logger.warning("No hay template HTML disponible")
            self.preview_panel.label_preview.setText("Error: No hay template HTML cargado")
            return
        
        if not html_template.ruta_html:
            logger.warning("El template HTML no tiene ruta definida")
            self.preview_panel.label_preview.setText("Error: Template HTML sin ruta")
            return
        
        # Verificar que el archivo existe
        ruta_path = Path(html_template.ruta_html)
        if not ruta_path.exists():
            logger.error(f"El archivo HTML no existe: {html_template.ruta_html}")
            self.preview_panel.label_preview.setText(f"Error: Archivo HTML no encontrado: {ruta_path.name}")
            return
        
        # Obtener variables del panel de controles (editadas por usuario)
        variables_usuario = self.controls_panel.obtener_variables_html()
        
        # Obtener todas las variables detectadas en el template
        variables_template = html_template.detectar_variables()
        
        # Preparar variables (combinar datos del empleado con variables del usuario)
        variables = {}
        
        # Variables automáticas (vienen de la base de datos)
        if self.empleado_actual:
            # Desempaquetar: puede ser 6, 7 u 8 elementos
            if len(self.empleado_actual) >= 8:
                id_db, codigo_barras, id_unico, fecha_creacion, nombre_empleado, descripcion, formato, nombre_archivo = self.empleado_actual
            elif len(self.empleado_actual) >= 7:
                id_db, codigo_barras, id_unico, nombre_empleado, descripcion, formato, nombre_archivo = self.empleado_actual
            elif len(self.empleado_actual) >= 6:
                id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = self.empleado_actual
                descripcion = ""
            else:
                descripcion = ""
                nombre_empleado = "SIN NOMBRE"
                id_unico = ""
                nombre_archivo = ""
            
            nombre = nombre_empleado or "SIN NOMBRE"
            codigo_path = IMAGES_DIR / nombre_archivo if nombre_archivo else Path("")
            
            # ID único siempre se obtiene del empleado
            if "id_unico" in variables_template:
                variables["id_unico"] = id_unico or ""
                # Actualizar campo en la UI si existe
                if "id_unico" in self.controls_panel.campos_variables:
                    campo_id = self.controls_panel.campos_variables["id_unico"]
                    if not isinstance(campo_id, dict):
                        campo_id.setText(id_unico or "")
            
            # Código de barras como imagen
            if "codigo_barras" in variables_template:
                variables["codigo_barras"] = codigo_path if codigo_path and codigo_path.exists() else Path("")
                # Actualizar campo en la UI si existe
                if "codigo_barras" in self.controls_panel.campos_variables:
                    campo_codigo = self.controls_panel.campos_variables["codigo_barras"]
                    if isinstance(campo_codigo, dict) and "campo" in campo_codigo:
                        if codigo_path.exists():
                            campo_codigo["campo"].setText(str(codigo_path))
                        else:
                            campo_codigo["campo"].setText("No disponible")
            
            # Nombre por defecto del empleado (puede ser sobrescrito por usuario)
            if "nombre" in variables_template:
                variables["nombre"] = variables_usuario.get("nombre", nombre) or nombre
            
            # Código de empleado (descripcion)
            if "descripcion" in variables_template:
                variables["descripcion"] = variables_usuario.get("descripcion", descripcion) or descripcion
        else:
            # Datos de ejemplo
            if "id_unico" in variables_template:
                variables["id_unico"] = "EJEMPLO123"
                if "id_unico" in self.controls_panel.campos_variables:
                    campo_id = self.controls_panel.campos_variables["id_unico"]
                    if not isinstance(campo_id, dict):
                        campo_id.setText("EJEMPLO123")
            if "codigo_barras" in variables_template:
                variables["codigo_barras"] = Path("")
                if "codigo_barras" in self.controls_panel.campos_variables:
                    campo_codigo = self.controls_panel.campos_variables["codigo_barras"]
                    if isinstance(campo_codigo, dict) and "campo" in campo_codigo:
                        campo_codigo["campo"].setText("No disponible (ejemplo)")
            if "nombre" in variables_template:
                variables["nombre"] = variables_usuario.get("nombre", "EJEMPLO") or "EJEMPLO"
        
        # Foto siempre vacía por ahora
        if "foto" in variables_template:
            variables["foto"] = Path("")
        
        # Logo: puede ser cargado por el usuario
        if "logo" in variables_template:
            logo_path = variables_usuario.get("logo")
            if logo_path and isinstance(logo_path, Path) and logo_path.exists():
                variables["logo"] = logo_path
            else:
                variables["logo"] = Path("")
        
        # Agregar todas las variables editables del usuario
        for var in variables_template:
            if var not in {"id_unico", "codigo_barras", "foto", "logo"}:  # Estas se manejan automáticamente
                if var not in variables:  # Solo si no se estableció antes
                    valor = variables_usuario.get(var, "")
                    # Si es un Path, mantenerlo; si es string, usar el texto
                    if isinstance(valor, Path):
                        variables[var] = valor
                    else:
                        variables[var] = str(valor) or ""
        
        # Valores por defecto para variables comunes si están vacías
        valores_default = {
            "empresa": "Mi Empresa",
            "web": "www.ejemplo.com"
        }
        for var, default in valores_default.items():
            if var in variables_template and (not variables.get(var) or variables[var] == ""):
                variables[var] = default
        
        # Mostrar HTML directamente en la vista previa (sin renderizar a imagen)
        try:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Cargando HTML desde: {html_template.ruta_html}")
            logger.info(f"Variables: {variables}")
            
            # Leer HTML y inyectar variables
            ruta_path = Path(html_template.ruta_html)
            html_content = ruta_path.read_text(encoding='utf-8')
            
            # Inyectar variables usando el renderizador
            html_content = self.html_renderer._inyectar_variables(html_content, variables)
            
            # Mostrar HTML directamente en la vista previa
            self.preview_panel.actualizar_preview_html(
                html_content=html_content,
                ancho=html_template.ancho,
                alto=html_template.alto
            )
            
            logger.info("HTML cargado en vista previa exitosamente")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al cargar HTML en vista previa: {e}", exc_info=True)
            if hasattr(self.preview_panel, 'label_preview'):
                self.preview_panel.label_preview.setText(f"Error: {str(e)}")
                self.preview_panel.label_preview.show()
    
    def _actualizar_vista_previa_pil(self):
        """Actualiza la vista previa usando template PIL (sistema antiguo)"""
        if not self.empleado_actual:
            nombre = "EJEMPLO"
            codigo_path = None
        else:
            # Desempaquetar: puede ser 6, 7 u 8 elementos
            if len(self.empleado_actual) >= 8:
                id_db, codigo_barras, id_unico, fecha_creacion, nombre_empleado, descripcion, formato, nombre_archivo = self.empleado_actual
            elif len(self.empleado_actual) >= 7:
                id_db, codigo_barras, id_unico, nombre_empleado, descripcion, formato, nombre_archivo = self.empleado_actual
            elif len(self.empleado_actual) >= 6:
                id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = self.empleado_actual
            else:
                nombre = "SIN NOMBRE"
                codigo_path = None
                return
            
            nombre = nombre_empleado or "SIN NOMBRE"
            codigo_path = IMAGES_DIR / nombre_archivo
        
        # Obtener template actualizado
        template = self.controls_panel.obtener_template_actualizado()
        
        # Renderizar carnet
        try:
            imagen = self.designer.renderizar_carnet(
                template=template,
                nombre_empleado=nombre,
                codigo_barras_path=str(codigo_path) if codigo_path and codigo_path.exists() else None,
                empresa=template.empresa_texto if template.mostrar_empresa else None,
                web=template.web_texto if template.mostrar_web else None
            )
            self.preview_panel.actualizar_preview(imagen)
        except Exception as e:
            QMessageBox.warning(
                self.employees_panel,
                "Error",
                f"Error al generar vista previa: {str(e)}"
            )
    
    def mostrar_vista_previa_empleado(self):
        """Muestra la vista previa del empleado seleccionado"""
        empleado = self.employees_panel.obtener_empleado_seleccionado()
        if not empleado:
            QMessageBox.warning(
                self.employees_panel,
                "Advertencia",
                "Por favor seleccione un empleado de la lista"
            )
            return
        
        self.empleado_actual = empleado
        self.actualizar_vista_previa()
    
    def generar_carnet_individual(self):
        """Genera un carnet para el empleado seleccionado"""
        empleado = self.employees_panel.obtener_empleado_seleccionado()
        if not empleado:
            QMessageBox.warning(
                self.employees_panel,
                "Advertencia",
                "Por favor seleccione un empleado de la lista"
            )
            return
        
        # Desempaquetar para obtener datos del empleado antes del diálogo
        if len(empleado) >= 8:
            id_db, codigo_barras, id_unico, fecha_creacion, nombre_empleado, descripcion, formato, nombre_archivo = empleado
        elif len(empleado) >= 7:
            id_db, codigo_barras, id_unico, nombre_empleado, descripcion, formato, nombre_archivo = empleado
        elif len(empleado) >= 6:
            id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = empleado
            descripcion = ""
        else:
            QMessageBox.warning(
                self.employees_panel,
                "Error",
                "Datos de empleado incompletos"
            )
            return
        
        # Pedir al usuario dónde guardar el PNG
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        from src.utils.file_utils import limpiar_nombre_archivo
        nombre_limpio = limpiar_nombre_archivo(nombre_empleado or "sin_nombre")
        nombre_png_default = f"carnet_{nombre_limpio}_{id_unico}_{fecha_hora}.png"
        
        ruta_png, _ = QFileDialog.getSaveFileName(
            self.employees_panel,
            "Guardar Carnet en PNG",
            nombre_png_default,
            "Archivos PNG (*.png);;Todos los archivos (*)"
        )
        
        if not ruta_png:
            return
        
        # Asegurar que tenga extensión .png
        ruta_png_path = Path(ruta_png)
        if ruta_png_path.suffix.lower() != '.png':
            ruta_png_path = ruta_png_path.with_suffix('.png')
        
        # Mostrar diálogo de progreso
        from src.views.widgets.progress_dialog import ProgressDialog
        progress = ProgressDialog("Generando Carnet PNG", self.employees_panel)
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.actualizar_progreso(0, 1, "Preparando generación...")
        progress.show()
        QApplication.processEvents()
        
        # Ruta del código de barras
        codigo_path = IMAGES_DIR / nombre_archivo
        if not codigo_path.exists():
            QMessageBox.warning(
                self.employees_panel,
                "Error",
                f"No se encontró la imagen del código de barras: {nombre_archivo}"
            )
            return
        
        # Verificar si se está usando template HTML
        if self.controls_panel.usar_template_html():
            # Usar renderizado HTML (igual que la vista previa)
            try:
                html_template = self.controls_panel.obtener_html_template()
                if not html_template:
                    QMessageBox.warning(
                        self.employees_panel,
                        "Error",
                        "No hay template HTML cargado"
                    )
                    return
                
                # Preparar variables (igual que en _actualizar_vista_previa_html)
                variables_usuario = self.controls_panel.obtener_variables_html()
                variables_template = html_template.detectar_variables()
                variables = {}
                
                # Datos del empleado
                nombre = nombre_empleado or "SIN NOMBRE"
                if "id_unico" in variables_template:
                    variables["id_unico"] = id_unico
                if "codigo_barras" in variables_template:
                    variables["codigo_barras"] = codigo_path
                if "nombre" in variables_template:
                    variables["nombre"] = variables_usuario.get("nombre", nombre) or nombre
                if "descripcion" in variables_template:
                    variables["descripcion"] = variables_usuario.get("descripcion", descripcion) or descripcion
                
                # Logo y foto
                if "logo" in variables_template:
                    logo_path = variables_usuario.get("logo")
                    if logo_path and isinstance(logo_path, Path) and logo_path.exists():
                        variables["logo"] = logo_path
                    else:
                        variables["logo"] = Path("")
                if "foto" in variables_template:
                    variables["foto"] = Path("")
                
                # Otras variables del usuario
                for var in variables_template:
                    if var not in {"id_unico", "codigo_barras", "foto", "logo", "nombre"}:
                        if var not in variables:
                            valor = variables_usuario.get(var, "")
                            if isinstance(valor, Path):
                                variables[var] = valor
                            else:
                                variables[var] = str(valor) or ""
                
                # Valores por defecto
                valores_default = {
                    "empresa": "Mi Empresa",
                    "web": "www.ejemplo.com"
                }
                for var, default in valores_default.items():
                    if var in variables_template and (not variables.get(var) or variables[var] == ""):
                        variables[var] = default
                
                # Leer HTML y renderizar
                html_content = Path(html_template.ruta_html).read_text(encoding='utf-8')
                html_content = self.html_renderer._inyectar_variables(html_content, variables)
                
                # Logging para debug
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Renderizando carnet HTML para {nombre_empleado}")
                logger.info(f"Variables inyectadas: {list(variables.keys())}")
                logger.info(f"Tamaño del HTML: {len(html_content)} caracteres")
                
                progress.actualizar_progreso(0, 1, "Renderizando carnet en alta calidad...")
                QApplication.processEvents()
                
                # Asegurar que el widget esté completamente inicializado antes del primer renderizado
                # Esto es crítico para evitar imágenes en blanco en el primer intento
                if not self.html_renderer._inicializado:
                    # Esperar un momento adicional para la inicialización completa
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(200, lambda: None)
                    QApplication.processEvents()
                
                # Renderizar HTML a imagen con alta calidad (600 DPI)
                # Las mejoras de sincronización ya están implementadas en html_renderer.py
                imagen = self.html_renderer.renderizar_html_a_imagen(
                    html_content=html_content,
                    ancho=html_template.ancho,
                    alto=html_template.alto,
                    dpi=600  # Alta calidad para impresión profesional
                )
                
                if imagen:
                    logger.info(f"Imagen renderizada exitosamente: {imagen.size}")
                    
                    # Verificar que la imagen no esté completamente en blanco antes de guardar
                    # Muestrear algunos píxeles para verificar que tenga contenido
                    ancho_img, alto_img = imagen.size
                    if ancho_img > 100 and alto_img > 100:
                        # Verificar algunos píxeles aleatorios
                        from PIL import ImageStat
                        stat = ImageStat.Stat(imagen)
                        # Si todos los canales tienen el mismo valor y es blanco (255), probablemente está en blanco
                        if len(stat.mean) >= 3:
                            media_r, media_g, media_b = stat.mean[0], stat.mean[1], stat.mean[2]
                            # Si la media es muy cercana a 255 en todos los canales, está en blanco
                            if media_r > 250 and media_g > 250 and media_b > 250:
                                logger.warning("La imagen renderizada parece estar completamente en blanco")
                                # Intentar renderizar nuevamente con más tiempo
                                progress.actualizar_progreso(0, 1, "Reintentando renderizado...")
                                QApplication.processEvents()
                                
                                # Esperar un momento adicional
                                from PyQt6.QtCore import QTimer
                                QTimer.singleShot(1000, lambda: None)
                                QApplication.processEvents()
                                
                                # Re-renderizar
                                imagen = self.html_renderer.renderizar_html_a_imagen(
                                    html_content=html_content,
                                    ancho=html_template.ancho,
                                    alto=html_template.alto,
                                    dpi=600
                                )
                                
                                if not imagen:
                                    progress.close()
                                    QMessageBox.warning(
                                        self.employees_panel,
                                        "Error",
                                        "No se pudo renderizar el carnet desde el HTML después del reintento"
                                    )
                                    return
                else:
                    logger.error("No se pudo renderizar la imagen desde HTML")
                
                if not imagen:
                    progress.close()
                    QMessageBox.warning(
                        self.employees_panel,
                        "Error",
                        "No se pudo renderizar el carnet desde el HTML"
                    )
                    return
                
                progress.actualizar_progreso(0, 1, "Guardando carnet...")
                QApplication.processEvents()
                
                # Guardar carnet con máxima calidad PNG en la ubicación elegida por el usuario
                # Guardar con máxima calidad (600 DPI, sin optimización, compresión mínima)
                imagen.save(ruta_png_path, "PNG", dpi=(600, 600), optimize=False, compress_level=1)
                
                progress.actualizar_progreso(1, 1, "¡Carnet generado exitosamente!")
                QApplication.processEvents()
                progress.close()
                
                QMessageBox.information(
                    self.employees_panel,
                    "Éxito",
                    f"Carnet PNG generado exitosamente:\n{ruta_png_path}"
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error al generar carnet HTML: {e}", exc_info=True)
                QMessageBox.critical(
                    self.employees_panel,
                    "Error",
                    f"Error al generar carnet: {str(e)}"
                )
        else:
            # Usar sistema PIL antiguo
            try:
                template = self.controls_panel.obtener_template_actualizado()
                imagen = self.designer.renderizar_carnet(
                    template=template,
                    nombre_empleado=nombre_empleado or "SIN NOMBRE",
                    codigo_barras_path=str(codigo_path),
                    empresa=template.empresa_texto if template.mostrar_empresa else None,
                    web=template.web_texto if template.mostrar_web else None
                )
                
                progress.actualizar_progreso(0, 1, "Guardando carnet...")
                QApplication.processEvents()
                
                # Guardar carnet en la ubicación elegida por el usuario
                if self.designer.guardar_carnet(imagen, ruta_png_path):
                    progress.actualizar_progreso(1, 1, "¡Carnet generado exitosamente!")
                    QApplication.processEvents()
                    progress.close()
                    QMessageBox.information(
                        self.employees_panel,
                        "Éxito",
                        f"Carnet PNG generado exitosamente:\n{ruta_png_path}"
                    )
                else:
                    progress.close()
                    QMessageBox.warning(
                        self.employees_panel,
                        "Error",
                        "No se pudo guardar el carnet"
                    )
            except Exception as e:
                progress.close()
                QMessageBox.critical(
                    self.employees_panel,
                    "Error",
                    f"Error al generar carnet: {str(e)}"
                )
    
    def generar_carnets_masivos(self):
        """Genera carnets para todos los empleados de la lista y los guarda en un ZIP"""
        empleados = self.employees_panel.obtener_todos_empleados()
        
        if not empleados:
            QMessageBox.warning(
                self.employees_panel,
                "Advertencia",
                "No hay empleados en la lista para generar carnets"
            )
            return
        
        respuesta = QMessageBox.question(
            self.employees_panel,
            "Confirmar",
            f"¿Desea generar {len(empleados)} carnet(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        
        # Pedir al usuario dónde guardar el ZIP
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_zip_default = f"carnets_masivos_{fecha_hora}.zip"
        
        ruta_zip, _ = QFileDialog.getSaveFileName(
            self.employees_panel,
            "Guardar Carnets en ZIP",
            nombre_zip_default,
            "Archivos ZIP (*.zip);;Todos los archivos (*)"
        )
        
        if not ruta_zip:
            return
        
        # Asegurar que tenga extensión .zip
        ruta_zip_path = Path(ruta_zip)
        if ruta_zip_path.suffix.lower() != '.zip':
            ruta_zip_path = ruta_zip_path.with_suffix('.zip')
        
        # Mostrar diálogo de progreso
        from src.views.widgets.progress_dialog import ProgressDialog
        progress = ProgressDialog("Generando Carnets Masivos", self.employees_panel)
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.show()
        QApplication.processEvents()
        
        exitosos = 0
        errores = 0
        total = len(empleados)
        
        # Crear directorio temporal para almacenar carnets antes de comprimir
        directorio_temp = None
        archivos_generados = []
        
        try:
            directorio_temp = Path(tempfile.mkdtemp(prefix="carnets_temp_"))
            
            # Verificar si se está usando template HTML
            usar_html = self.controls_panel.usar_template_html()
            
            if usar_html:
                # Preparar variables del usuario una sola vez
                html_template = self.controls_panel.obtener_html_template()
                if not html_template:
                    QMessageBox.warning(
                        self.employees_panel,
                        "Error",
                        "No hay template HTML cargado"
                    )
                    return
                
                variables_usuario = self.controls_panel.obtener_variables_html()
                variables_template = html_template.detectar_variables()
                
                # Leer HTML base una sola vez
                html_base = Path(html_template.ruta_html).read_text(encoding='utf-8')
                
                # Valores por defecto
                valores_default = {
                    "empresa": "Mi Empresa",
                    "web": "www.ejemplo.com"
                }
            else:
                # Obtener template PIL
                template = self.controls_panel.obtener_template_actualizado()
            
            for indice, empleado in enumerate(empleados, 1):
                # Actualizar progreso
                nombre_empleado_temp = ""
                try:
                    if len(empleado) >= 5:
                        nombre_empleado_temp = empleado[4] if len(empleado) >= 5 else "empleado"
                except:
                    nombre_empleado_temp = "empleado"
                
                faltantes = total - indice + 1
                progress.actualizar_progreso(
                    indice - 1, 
                    total, 
                    f"Generando carnet {indice} de {total}\nFaltan {faltantes} carnet(s) por generar\nEmpleado: {nombre_empleado_temp}"
                )
                QApplication.processEvents()
                try:
                    # Desempaquetar: id, codigo_barras, id_unico, fecha_creacion, nombre_empleado, descripcion, formato, nombre_archivo
                    if len(empleado) >= 8:
                        id_db, codigo_barras, id_unico, fecha_creacion, nombre_empleado, descripcion, formato, nombre_archivo = empleado
                    elif len(empleado) >= 6:
                        # Compatibilidad con formato anterior
                        id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = empleado
                        descripcion = ""
                    else:
                        errores += 1
                        continue
                    
                    codigo_path = IMAGES_DIR / nombre_archivo
                    if not codigo_path.exists():
                        errores += 1
                        continue
                    
                    if usar_html:
                        # Usar renderizado HTML
                        variables = {}
                        
                        # Datos del empleado
                        nombre = nombre_empleado or "SIN NOMBRE"
                        if "id_unico" in variables_template:
                            variables["id_unico"] = id_unico
                        if "codigo_barras" in variables_template:
                            variables["codigo_barras"] = codigo_path
                        if "nombre" in variables_template:
                            variables["nombre"] = variables_usuario.get("nombre", nombre) or nombre
                        if "descripcion" in variables_template:
                            variables["descripcion"] = variables_usuario.get("descripcion", descripcion) or descripcion
                        
                        # Logo y foto
                        if "logo" in variables_template:
                            logo_path = variables_usuario.get("logo")
                            if logo_path and isinstance(logo_path, Path) and logo_path.exists():
                                variables["logo"] = logo_path
                            else:
                                variables["logo"] = Path("")
                        if "foto" in variables_template:
                            variables["foto"] = Path("")
                        
                        # Otras variables del usuario
                        for var in variables_template:
                            if var not in {"id_unico", "codigo_barras", "foto", "logo", "nombre"}:
                                if var not in variables:
                                    valor = variables_usuario.get(var, "")
                                    if isinstance(valor, Path):
                                        variables[var] = valor
                                    else:
                                        variables[var] = str(valor) or ""
                        
                        # Aplicar valores por defecto
                        for var, default in valores_default.items():
                            if var in variables_template and (not variables.get(var) or variables[var] == ""):
                                variables[var] = default
                        
                        # Inyectar variables en HTML
                        html_content = self.html_renderer._inyectar_variables(html_base, variables)
                        
                        # Renderizar HTML a imagen con alta calidad (600 DPI)
                        imagen = self.html_renderer.renderizar_html_a_imagen(
                            html_content=html_content,
                            ancho=html_template.ancho,
                            alto=html_template.alto,
                            dpi=600  # Alta calidad para impresión profesional
                        )
                        
                        if not imagen:
                            errores += 1
                            continue
                        
                        # Guardar carnet en directorio temporal
                        from src.utils.file_utils import limpiar_nombre_archivo
                        nombre_limpio = limpiar_nombre_archivo(nombre_empleado or "sin_nombre")
                        nombre_archivo_carnet = f"carnet_{nombre_limpio}_{id_unico}.png"
                        ruta_carnet = directorio_temp / nombre_archivo_carnet
                        
                        # Guardar con máxima calidad PNG
                        imagen.save(ruta_carnet, "PNG", dpi=(600, 600), optimize=False, compress_level=1)
                        archivos_generados.append(ruta_carnet)
                        exitosos += 1
                    else:
                        # Usar sistema PIL antiguo
                        imagen = self.designer.renderizar_carnet(
                            template=template,
                            nombre_empleado=nombre_empleado or "SIN NOMBRE",
                            codigo_barras_path=str(codigo_path),
                            empresa=template.empresa_texto if template.mostrar_empresa else None,
                            web=template.web_texto if template.mostrar_web else None
                        )
                        
                        from src.utils.file_utils import limpiar_nombre_archivo
                        nombre_limpio = limpiar_nombre_archivo(nombre_empleado or "sin_nombre")
                        nombre_archivo_carnet = f"carnet_{nombre_limpio}_{id_unico}.png"
                        ruta_carnet = directorio_temp / nombre_archivo_carnet
                        
                        if self.designer.guardar_carnet(imagen, ruta_carnet):
                            archivos_generados.append(ruta_carnet)
                            exitosos += 1
                        else:
                            errores += 1
                except Exception as e:
                    errores += 1
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error al generar carnet para {nombre_empleado}: {e}")
            
            # Crear archivo ZIP con todos los carnets generados
            if archivos_generados:
                progress.actualizar_progreso(total, total + 1, "Comprimiendo carnets en ZIP...")
                QApplication.processEvents()
                
                try:
                    with zipfile.ZipFile(str(ruta_zip_path), 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for ruta_carnet in archivos_generados:
                            if ruta_carnet.exists():
                                # Agregar al ZIP con el nombre del archivo (sin la ruta completa)
                                zipf.write(str(ruta_carnet), ruta_carnet.name)
                    
                    progress.actualizar_progreso(total + 1, total + 1, "¡ZIP creado exitosamente!")
                    QApplication.processEvents()
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error al crear ZIP: {e}")
                    QMessageBox.critical(
                        self.employees_panel,
                        "Error",
                        f"Error al crear el archivo ZIP:\n{str(e)}"
                    )
                    return
        finally:
            # Limpiar directorio temporal
            if directorio_temp and directorio_temp.exists():
                try:
                    import shutil
                    shutil.rmtree(directorio_temp)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"No se pudo eliminar el directorio temporal: {e}")
        
        # Cerrar diálogo de progreso
        progress.close()
        
        mensaje = f"Generación completada:\n{exitosos} carnet(s) generado(s) y guardado(s) en:\n{ruta_zip_path}"
        if errores > 0:
            mensaje += f"\n\n{errores} error(es)"
        
        QMessageBox.information(self.employees_panel, "Resultado", mensaje)
    
    def generar_carnet_individual_pdf(self):
        """Genera un carnet en formato PDF de alta calidad para el empleado seleccionado"""
        empleado = self.employees_panel.obtener_empleado_seleccionado()
        if not empleado:
            QMessageBox.warning(
                self.employees_panel,
                "Advertencia",
                "Por favor seleccione un empleado de la lista"
            )
            return
        
        # Pedir al usuario dónde guardar el PDF
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_empleado_temp = empleado[3] if len(empleado) >= 4 else "empleado"
        from src.utils.file_utils import limpiar_nombre_archivo
        nombre_limpio = limpiar_nombre_archivo(nombre_empleado_temp)
        id_unico_temp = empleado[2] if len(empleado) >= 3 else ""
        nombre_pdf_default = f"carnet_{nombre_limpio}_{id_unico_temp}_{fecha_hora}.pdf"
        
        ruta_pdf, _ = QFileDialog.getSaveFileName(
            self.employees_panel,
            "Guardar Carnet en PDF",
            nombre_pdf_default,
            "Archivos PDF (*.pdf);;Todos los archivos (*)"
        )
        
        if not ruta_pdf:
            return
        
        # Asegurar que tenga extensión .pdf
        ruta_pdf_path = Path(ruta_pdf)
        if ruta_pdf_path.suffix.lower() != '.pdf':
            ruta_pdf_path = ruta_pdf_path.with_suffix('.pdf')
        
        # Mostrar diálogo de progreso
        from src.views.widgets.progress_dialog import ProgressDialog
        progress = ProgressDialog("Generando Carnet PDF", self.employees_panel)
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.actualizar_progreso(0, 1, "Preparando generación...")
        progress.show()
        QApplication.processEvents()
        
        # Desempaquetar datos del empleado
        if len(empleado) >= 8:
            id_db, codigo_barras, id_unico, fecha_creacion, nombre_empleado, descripcion, formato, nombre_archivo = empleado
        elif len(empleado) >= 7:
            id_db, codigo_barras, id_unico, nombre_empleado, descripcion, formato, nombre_archivo = empleado
        elif len(empleado) >= 6:
            id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = empleado
            descripcion = ""
        else:
            progress.close()
            QMessageBox.warning(
                self.employees_panel,
                "Error",
                "Datos de empleado incompletos"
            )
            return
        
        codigo_path = IMAGES_DIR / nombre_archivo
        if not codigo_path.exists():
            progress.close()
            QMessageBox.warning(
                self.employees_panel,
                "Error",
                f"No se encontró la imagen del código de barras: {nombre_archivo}"
            )
            return
        
        try:
            # Verificar si se está usando template HTML
            if self.controls_panel.usar_template_html():
                html_template = self.controls_panel.obtener_html_template()
                if not html_template:
                    progress.close()
                    QMessageBox.warning(
                        self.employees_panel,
                        "Error",
                        "No hay template HTML cargado"
                    )
                    return
                
                # Preparar variables
                variables_usuario = self.controls_panel.obtener_variables_html()
                variables_template = html_template.detectar_variables()
                variables = {}
                
                nombre = nombre_empleado or "SIN NOMBRE"
                if "id_unico" in variables_template:
                    variables["id_unico"] = id_unico
                if "codigo_barras" in variables_template:
                    variables["codigo_barras"] = codigo_path
                if "nombre" in variables_template:
                    variables["nombre"] = variables_usuario.get("nombre", nombre) or nombre
                if "descripcion" in variables_template:
                    variables["descripcion"] = variables_usuario.get("descripcion", descripcion) or descripcion
                
                # Logo y foto
                if "logo" in variables_template:
                    logo_path = variables_usuario.get("logo")
                    if logo_path and isinstance(logo_path, Path) and logo_path.exists():
                        variables["logo"] = logo_path
                    else:
                        variables["logo"] = Path("")
                if "foto" in variables_template:
                    variables["foto"] = Path("")
                
                # Otras variables
                for var in variables_template:
                    if var not in {"id_unico", "codigo_barras", "foto", "logo", "nombre"}:
                        if var not in variables:
                            valor = variables_usuario.get(var, "")
                            if isinstance(valor, Path):
                                variables[var] = valor
                            else:
                                variables[var] = str(valor) or ""
                
                # Valores por defecto
                valores_default = {
                    "empresa": "Mi Empresa",
                    "web": "www.ejemplo.com"
                }
                for var, default in valores_default.items():
                    if var in variables_template and (not variables.get(var) or variables[var] == ""):
                        variables[var] = default
                
                # Leer HTML y renderizar
                html_content = Path(html_template.ruta_html).read_text(encoding='utf-8')
                html_content = self.html_renderer._inyectar_variables(html_content, variables)
                
                progress.actualizar_progreso(0, 1, "Renderizando carnet en alta calidad...")
                QApplication.processEvents()
                
                # Renderizar a máxima calidad (1200 DPI para PDF de super mega calidad)
                imagen = self.html_renderer.renderizar_html_a_imagen(
                    html_content=html_content,
                    ancho=html_template.ancho,
                    alto=html_template.alto,
                    dpi=1200  # Super mega calidad para PDF
                )
            else:
                # Usar sistema PIL
                template = self.controls_panel.obtener_template_actualizado()
                progress.actualizar_progreso(0, 1, "Renderizando carnet...")
                QApplication.processEvents()
                
                imagen = self.designer.renderizar_carnet(
                    template=template,
                    nombre_empleado=nombre_empleado or "SIN NOMBRE",
                    codigo_barras_path=str(codigo_path),
                    empresa=template.empresa_texto if template.mostrar_empresa else None,
                    web=template.web_texto if template.mostrar_web else None
                )
                
                # Escalar imagen para alta calidad PDF (1200 DPI)
                factor_calidad = 1200 / 300.0  # 4x más grande
                nuevo_ancho = int(imagen.size[0] * factor_calidad)
                nuevo_alto = int(imagen.size[1] * factor_calidad)
                imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            
            if not imagen:
                progress.close()
                QMessageBox.warning(
                    self.employees_panel,
                    "Error",
                    "No se pudo renderizar el carnet"
                )
                return
            
            progress.actualizar_progreso(0, 1, "Guardando PDF en alta calidad...")
            QApplication.processEvents()
            
            # Guardar como PDF con máxima calidad
            # Convertir a RGB si es necesario (PDF requiere RGB)
            if imagen.mode != 'RGB':
                imagen = imagen.convert('RGB')
            
            # Guardar PDF con máxima calidad
            imagen.save(
                ruta_pdf_path,
                "PDF",
                resolution=1200.0,  # 1200 DPI para super mega calidad
                quality=100
            )
            
            progress.actualizar_progreso(1, 1, "¡PDF generado exitosamente!")
            QApplication.processEvents()
            progress.close()
            
            QMessageBox.information(
                self.employees_panel,
                "Éxito",
                f"Carnet PDF generado exitosamente:\n{ruta_pdf_path}"
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al generar carnet PDF: {e}", exc_info=True)
            progress.close()
            QMessageBox.critical(
                self.employees_panel,
                "Error",
                f"Error al generar carnet PDF: {str(e)}"
            )
    
    def generar_carnets_masivos_pdf(self):
        """Genera carnets en formato PDF de alta calidad para todos los empleados y los guarda en un ZIP"""
        empleados = self.employees_panel.obtener_todos_empleados()
        
        if not empleados:
            QMessageBox.warning(
                self.employees_panel,
                "Advertencia",
                "No hay empleados en la lista para generar carnets"
            )
            return
        
        respuesta = QMessageBox.question(
            self.employees_panel,
            "Confirmar",
            f"¿Desea generar {len(empleados)} carnet(s) en PDF?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        
        # Pedir al usuario dónde guardar el ZIP
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_zip_default = f"carnets_pdf_masivos_{fecha_hora}.zip"
        
        ruta_zip, _ = QFileDialog.getSaveFileName(
            self.employees_panel,
            "Guardar Carnets PDF en ZIP",
            nombre_zip_default,
            "Archivos ZIP (*.zip);;Todos los archivos (*)"
        )
        
        if not ruta_zip:
            return
        
        # Asegurar que tenga extensión .zip
        ruta_zip_path = Path(ruta_zip)
        if ruta_zip_path.suffix.lower() != '.zip':
            ruta_zip_path = ruta_zip_path.with_suffix('.zip')
        
        # Mostrar diálogo de progreso
        from src.views.widgets.progress_dialog import ProgressDialog
        progress = ProgressDialog("Generando Carnets PDF Masivos", self.employees_panel)
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.show()
        QApplication.processEvents()
        
        exitosos = 0
        errores = 0
        total = len(empleados)
        
        # Crear directorio temporal para almacenar PDFs antes de comprimir
        directorio_temp = None
        archivos_generados = []
        
        try:
            directorio_temp = Path(tempfile.mkdtemp(prefix="carnets_pdf_temp_"))
            
            # Verificar si se está usando template HTML
            usar_html = self.controls_panel.usar_template_html()
            
            if usar_html:
                html_template = self.controls_panel.obtener_html_template()
                if not html_template:
                    QMessageBox.warning(
                        self.employees_panel,
                        "Error",
                        "No hay template HTML cargado"
                    )
                    return
                
                variables_usuario = self.controls_panel.obtener_variables_html()
                variables_template = html_template.detectar_variables()
                html_base = Path(html_template.ruta_html).read_text(encoding='utf-8')
                
                valores_default = {
                    "empresa": "Mi Empresa",
                    "web": "www.ejemplo.com"
                }
            else:
                template = self.controls_panel.obtener_template_actualizado()
            
            for indice, empleado in enumerate(empleados, 1):
                nombre_empleado_temp = ""
                try:
                    if len(empleado) >= 5:
                        nombre_empleado_temp = empleado[4] if len(empleado) >= 5 else "empleado"
                except:
                    nombre_empleado_temp = "empleado"
                
                faltantes = total - indice + 1
                progress.actualizar_progreso(
                    indice - 1,
                    total,
                    f"Generando PDF {indice} de {total}\nFaltan {faltantes} PDF(s) por generar\nEmpleado: {nombre_empleado_temp}"
                )
                QApplication.processEvents()
                
                try:
                    # Desempaquetar datos
                    if len(empleado) >= 8:
                        id_db, codigo_barras, id_unico, fecha_creacion, nombre_empleado, descripcion, formato, nombre_archivo = empleado
                    elif len(empleado) >= 6:
                        id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = empleado
                        descripcion = ""
                    else:
                        errores += 1
                        continue
                    
                    codigo_path = IMAGES_DIR / nombre_archivo
                    if not codigo_path.exists():
                        errores += 1
                        continue
                    
                    # Generar nombre del PDF en directorio temporal
                    from src.utils.file_utils import limpiar_nombre_archivo
                    nombre_limpio = limpiar_nombre_archivo(nombre_empleado or "sin_nombre")
                    nombre_pdf = f"carnet_{nombre_limpio}_{id_unico}.pdf"
                    ruta_pdf = directorio_temp / nombre_pdf
                    
                    if usar_html:
                        # Preparar variables
                        variables = {}
                        nombre = nombre_empleado or "SIN NOMBRE"
                        if "id_unico" in variables_template:
                            variables["id_unico"] = id_unico
                        if "codigo_barras" in variables_template:
                            variables["codigo_barras"] = codigo_path
                        if "nombre" in variables_template:
                            variables["nombre"] = variables_usuario.get("nombre", nombre) or nombre
                        if "descripcion" in variables_template:
                            variables["descripcion"] = variables_usuario.get("descripcion", descripcion) or descripcion
                        
                        # Logo y foto
                        if "logo" in variables_template:
                            logo_path = variables_usuario.get("logo")
                            if logo_path and isinstance(logo_path, Path) and logo_path.exists():
                                variables["logo"] = logo_path
                            else:
                                variables["logo"] = Path("")
                        if "foto" in variables_template:
                            variables["foto"] = Path("")
                        
                        # Otras variables
                        for var in variables_template:
                            if var not in {"id_unico", "codigo_barras", "foto", "logo", "nombre"}:
                                if var not in variables:
                                    valor = variables_usuario.get(var, "")
                                    if isinstance(valor, Path):
                                        variables[var] = valor
                                    else:
                                        variables[var] = str(valor) or ""
                        
                        # Aplicar valores por defecto
                        for var, default in valores_default.items():
                            if var in variables_template and (not variables.get(var) or variables[var] == ""):
                                variables[var] = default
                        
                        # Inyectar variables y renderizar
                        html_content = self.html_renderer._inyectar_variables(html_base, variables)
                        imagen = self.html_renderer.renderizar_html_a_imagen(
                            html_content=html_content,
                            ancho=html_template.ancho,
                            alto=html_template.alto,
                            dpi=1200  # Super mega calidad para PDF
                        )
                    else:
                        # Usar sistema PIL
                        imagen = self.designer.renderizar_carnet(
                            template=template,
                            nombre_empleado=nombre_empleado or "SIN NOMBRE",
                            codigo_barras_path=str(codigo_path),
                            empresa=template.empresa_texto if template.mostrar_empresa else None,
                            web=template.web_texto if template.mostrar_web else None
                        )
                        
                        # Escalar para alta calidad
                        factor_calidad = 1200 / 300.0
                        nuevo_ancho = int(imagen.size[0] * factor_calidad)
                        nuevo_alto = int(imagen.size[1] * factor_calidad)
                        imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
                    
                    if not imagen:
                        errores += 1
                        continue
                    
                    # Convertir a RGB si es necesario
                    if imagen.mode != 'RGB':
                        imagen = imagen.convert('RGB')
                    
                    # Guardar PDF con máxima calidad
                    imagen.save(
                        ruta_pdf,
                        "PDF",
                        resolution=1200.0,  # 1200 DPI para super mega calidad
                        quality=100
                    )
                    archivos_generados.append(ruta_pdf)
                    exitosos += 1
                except Exception as e:
                    errores += 1
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error al generar PDF para {nombre_empleado}: {e}")
            
            # Crear archivo ZIP con todos los PDFs generados
            if archivos_generados:
                progress.actualizar_progreso(total, total + 1, "Comprimiendo PDFs en ZIP...")
                QApplication.processEvents()
                
                try:
                    with zipfile.ZipFile(str(ruta_zip_path), 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for ruta_pdf in archivos_generados:
                            if ruta_pdf.exists():
                                # Agregar al ZIP con el nombre del archivo (sin la ruta completa)
                                zipf.write(str(ruta_pdf), ruta_pdf.name)
                    
                    progress.actualizar_progreso(total + 1, total + 1, "¡ZIP creado exitosamente!")
                    QApplication.processEvents()
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error al crear ZIP: {e}")
                    QMessageBox.critical(
                        self.employees_panel,
                        "Error",
                        f"Error al crear el archivo ZIP:\n{str(e)}"
                    )
                    return
        finally:
            # Limpiar directorio temporal
            if directorio_temp and directorio_temp.exists():
                try:
                    import shutil
                    shutil.rmtree(directorio_temp)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"No se pudo eliminar el directorio temporal: {e}")
        
        progress.actualizar_progreso(total + 1, total + 1, "¡Generación completada!")
        QApplication.processEvents()
        progress.close()
        
        mensaje = f"Generación completada:\n{exitosos} PDF(s) generado(s) y guardado(s) en:\n{ruta_zip_path}"
        if errores > 0:
            mensaje += f"\n\n{errores} error(es)"
        
        QMessageBox.information(self.employees_panel, "Resultado", mensaje)

