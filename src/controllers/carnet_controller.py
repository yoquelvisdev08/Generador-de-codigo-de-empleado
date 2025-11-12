"""
Controlador para el editor de carnet
"""
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QMessageBox, QFileDialog
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
        self.employees_panel.boton_exportar.clicked.connect(self.exportar_carnets)
        self.employees_panel.campo_busqueda.textChanged.connect(self.buscar_empleados)
    
    def _cargar_empleados(self):
        """Carga los empleados desde la base de datos"""
        empleados = self.db_manager.obtener_todos_codigos()
        self.employees_panel.cargar_empleados(empleados)
    
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
        
        id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = empleado
        
        # Actualizar campos de variables dinámicamente
        if nombre_empleado and "nombre" in self.controls_panel.campos_variables:
            self.controls_panel.campos_variables["nombre"].setText(nombre_empleado)
        
        # El ID único se usa automáticamente, no se edita
    
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
        
        # Variables automáticas (no editables)
        if self.empleado_actual:
            id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = self.empleado_actual
            nombre = nombre_empleado or "SIN NOMBRE"
            codigo_path = IMAGES_DIR / nombre_archivo
            
            # ID único siempre se obtiene del empleado
            if "id_unico" in variables_template:
                variables["id_unico"] = id_unico or ""
            
            # Código de barras como imagen
            if "codigo_barras" in variables_template:
                variables["codigo_barras"] = codigo_path if codigo_path and codigo_path.exists() else Path("")
            
            # Nombre por defecto del empleado (puede ser sobrescrito por usuario)
            if "nombre" in variables_template:
                variables["nombre"] = variables_usuario.get("nombre", nombre) or nombre
        else:
            # Datos de ejemplo
            if "id_unico" in variables_template:
                variables["id_unico"] = "EJEMPLO123"
            if "codigo_barras" in variables_template:
                variables["codigo_barras"] = Path("")
            if "nombre" in variables_template:
                variables["nombre"] = variables_usuario.get("nombre", "EJEMPLO") or "EJEMPLO"
        
        # Foto siempre vacía por ahora
        if "foto" in variables_template:
            variables["foto"] = Path("")
        
        # Agregar todas las variables editables del usuario
        for var in variables_template:
            if var not in {"id_unico", "codigo_barras", "foto"}:  # Estas se manejan automáticamente
                if var not in variables:  # Solo si no se estableció antes
                    variables[var] = variables_usuario.get(var, "") or ""
        
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
            id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = self.empleado_actual
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
        
        id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = empleado
        
        # Obtener template
        template = self.controls_panel.obtener_template_actualizado()
        
        # Ruta del código de barras
        codigo_path = IMAGES_DIR / nombre_archivo
        if not codigo_path.exists():
            QMessageBox.warning(
                self.employees_panel,
                "Error",
                f"No se encontró la imagen del código de barras: {nombre_archivo}"
            )
            return
        
        # Renderizar carnet
        try:
            imagen = self.designer.renderizar_carnet(
                template=template,
                nombre_empleado=nombre_empleado or "SIN NOMBRE",
                codigo_barras_path=str(codigo_path),
                empresa=template.empresa_texto if template.mostrar_empresa else None,
                web=template.web_texto if template.mostrar_web else None
            )
            
            # Guardar carnet
            from src.utils.file_utils import limpiar_nombre_archivo
            nombre_limpio = limpiar_nombre_archivo(nombre_empleado or "sin_nombre")
            nombre_archivo_carnet = f"carnet_{nombre_limpio}_{id_unico}.png"
            ruta_carnet = CARNETS_DIR / nombre_archivo_carnet
            
            if self.designer.guardar_carnet(imagen, ruta_carnet):
                QMessageBox.information(
                    self.employees_panel,
                    "Éxito",
                    f"Carnet generado exitosamente:\n{ruta_carnet}"
                )
            else:
                QMessageBox.warning(
                    self.employees_panel,
                    "Error",
                    "No se pudo guardar el carnet"
                )
        except Exception as e:
            QMessageBox.critical(
                self.employees_panel,
                "Error",
                f"Error al generar carnet: {str(e)}"
            )
    
    def generar_carnets_masivos(self):
        """Genera carnets para todos los empleados seleccionados"""
        empleados = self.employees_panel.obtener_empleados_seleccionados()
        
        if not empleados:
            QMessageBox.warning(
                self.employees_panel,
                "Advertencia",
                "Por favor seleccione uno o más empleados de la lista"
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
        
        # Obtener template
        template = self.controls_panel.obtener_template_actualizado()
        
        exitosos = 0
        errores = 0
        
        for empleado in empleados:
            try:
                id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = empleado
                
                codigo_path = IMAGES_DIR / nombre_archivo
                if not codigo_path.exists():
                    errores += 1
                    continue
                
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
                ruta_carnet = CARNETS_DIR / nombre_archivo_carnet
                
                if self.designer.guardar_carnet(imagen, ruta_carnet):
                    exitosos += 1
                else:
                    errores += 1
            except Exception as e:
                errores += 1
        
        mensaje = f"Generación completada:\n{exitosos} carnet(s) generado(s)"
        if errores > 0:
            mensaje += f"\n{errores} error(es)"
        
        QMessageBox.information(self.employees_panel, "Resultado", mensaje)
    
    def exportar_carnets(self):
        """Exporta los carnets generados"""
        if not CARNETS_DIR.exists() or not any(CARNETS_DIR.glob("*.png")):
            QMessageBox.warning(
                self.employees_panel,
                "Advertencia",
                "No hay carnets generados para exportar"
            )
            return
        
        directorio = QFileDialog.getExistingDirectory(
            self.employees_panel,
            "Seleccionar directorio para exportar"
        )
        
        if not directorio:
            return
        
        # Copiar carnets al directorio seleccionado
        import shutil
        copiados = 0
        
        for carnet in CARNETS_DIR.glob("*.png"):
            try:
                shutil.copy2(carnet, Path(directorio) / carnet.name)
                copiados += 1
            except Exception as e:
                pass
        
        QMessageBox.information(
            self.employees_panel,
            "Éxito",
            f"{copiados} carnet(s) exportado(s) a:\n{directorio}"
        )

