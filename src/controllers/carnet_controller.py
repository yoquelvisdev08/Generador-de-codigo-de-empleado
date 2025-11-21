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

# Importar OCRVerifier solo si está disponible
try:
    from src.services.ocr_verifier import OCRVerifier
    OCR_DISPONIBLE = True
except (ImportError, RuntimeError, OSError) as e:
    # Capturar errores de importación, inicialización o DLL
    OCRVerifier = None
    OCR_DISPONIBLE = False
    import logging
    logging.getLogger(__name__).warning(f"OCR no disponible: {e}")


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
        
        # Inicializar OCR solo si está disponible
        if OCR_DISPONIBLE:
            try:
                self.ocr_verifier = OCRVerifier()
                self.usar_ocr = True
                import logging
                logging.getLogger(__name__).info("✓ Verificación OCR (Tesseract) habilitada")
            except Exception as e:
                self.ocr_verifier = None
                self.usar_ocr = False
                import logging
                logger_ocr = logging.getLogger(__name__)
                logger_ocr.warning("=" * 60)
                logger_ocr.warning("⚠ OCR NO DISPONIBLE")
                logger_ocr.warning("=" * 60)
                logger_ocr.warning(f"Error: {e}")
                logger_ocr.warning("")
                logger_ocr.warning("SOLUCIÓN: Instala Visual C++ Redistributables:")
                logger_ocr.warning("https://aka.ms/vs/17/release/vc_redist.x64.exe")
                logger_ocr.warning("Luego reinicia la aplicación")
                logger_ocr.warning("=" * 60)
        else:
            self.ocr_verifier = None
            self.usar_ocr = False
            import logging
            logging.getLogger(__name__).warning("⚠ OCR no disponible - generación sin verificación. Instala 'pytesseract' y Tesseract OCR para habilitar verificación.")
        
        self.empleado_actual = None
        self._conectar_senales()
        self._cargar_empleados()
        # Establecer callback para actualización cuando cambien variables
        self.controls_panel.establecer_callback_actualizacion(self.actualizar_vista_previa)
        # Actualizar vista previa inicial después de un breve delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self.actualizar_vista_previa)
    
    def _desempaquetar_empleado(self, empleado):
        """
        Desempaqueta los datos del empleado de manera consistente
        
        Args:
            empleado: Tupla con datos del empleado
            
        Returns:
            dict con los datos del empleado: id_db, codigo_barras, id_unico, nombres, apellidos, 
            descripcion, formato, nombre_archivo, nombre_empleado (completo)
        """
        if not empleado:
            return None
        
        # Formato nuevo: (id, codigo_barras, id_unico, nombres, apellidos, descripcion, formato, nombre_archivo)
        # Formato antiguo con fecha: (id, codigo_barras, id_unico, fecha_creacion, nombre_empleado, descripcion, formato, nombre_archivo)
        # Formato antiguo sin fecha: (id, codigo_barras, id_unico, nombre_empleado, descripcion, formato, nombre_archivo)
        
        resultado = {
            'id_db': None,
            'codigo_barras': None,
            'id_unico': None,
            'nombres': '',
            'apellidos': '',
            'descripcion': '',
            'formato': '',
            'nombre_archivo': '',
            'nombre_empleado': ''  # nombre completo
        }
        
        try:
            if len(empleado) >= 9:
                # Nuevo formato con nombres y apellidos separados (con fecha_creacion)
                id_db, codigo_barras, id_unico, fecha_creacion, nombres, apellidos, descripcion, formato, nombre_archivo = empleado
                resultado['id_db'] = id_db
                resultado['codigo_barras'] = codigo_barras
                resultado['id_unico'] = id_unico
                resultado['nombres'] = nombres or ''
                resultado['apellidos'] = apellidos or ''
                resultado['descripcion'] = descripcion or ''
                resultado['formato'] = formato or ''
                resultado['nombre_archivo'] = nombre_archivo or ''
                resultado['nombre_empleado'] = f"{nombres or ''} {apellidos or ''}".strip()
            elif len(empleado) >= 8:
                # Puede ser formato nuevo sin fecha o formato antiguo con fecha
                # Intentamos detectar: si el índice 3 parece una fecha o un string corto, es formato antiguo
                # Formato nuevo: (id, codigo_barras, id_unico, nombres, apellidos, descripcion, formato, nombre_archivo)
                # Formato antiguo: (id, codigo_barras, id_unico, fecha_creacion, nombre_empleado, descripcion, formato, nombre_archivo)
                
                # Asumimos formato nuevo primero (sin fecha_creacion)
                id_db, codigo_barras, id_unico, nombres, apellidos, descripcion, formato, nombre_archivo = empleado
                
                # Si nombres y apellidos parecen correctos, es formato nuevo
                if isinstance(nombres, str) and isinstance(apellidos, str):
                    resultado['id_db'] = id_db
                    resultado['codigo_barras'] = codigo_barras
                    resultado['id_unico'] = id_unico
                    resultado['nombres'] = nombres or ''
                    resultado['apellidos'] = apellidos or ''
                    resultado['descripcion'] = descripcion or ''
                    resultado['formato'] = formato or ''
                    resultado['nombre_archivo'] = nombre_archivo or ''
                    resultado['nombre_empleado'] = f"{nombres or ''} {apellidos or ''}".strip()
                else:
                    # Es formato antiguo con fecha, re-desempaquetar
                    id_db, codigo_barras, id_unico, fecha_creacion, nombre_empleado, descripcion, formato, nombre_archivo = empleado
                    partes = nombre_empleado.strip().split()
                    if len(partes) >= 2:
                        nombres = partes[0]
                        apellidos = " ".join(partes[1:])
                    else:
                        nombres = nombre_empleado
                        apellidos = ''
                    
                    resultado['id_db'] = id_db
                    resultado['codigo_barras'] = codigo_barras
                    resultado['id_unico'] = id_unico
                    resultado['nombres'] = nombres
                    resultado['apellidos'] = apellidos
                    resultado['descripcion'] = descripcion or ''
                    resultado['formato'] = formato or ''
                    resultado['nombre_archivo'] = nombre_archivo or ''
                    resultado['nombre_empleado'] = nombre_empleado
            elif len(empleado) >= 7:
                # Formato antiguo sin fecha
                id_db, codigo_barras, id_unico, nombre_empleado, descripcion, formato, nombre_archivo = empleado
                partes = nombre_empleado.strip().split()
                if len(partes) >= 2:
                    nombres = partes[0]
                    apellidos = " ".join(partes[1:])
                else:
                    nombres = nombre_empleado
                    apellidos = ''
                
                resultado['id_db'] = id_db
                resultado['codigo_barras'] = codigo_barras
                resultado['id_unico'] = id_unico
                resultado['nombres'] = nombres
                resultado['apellidos'] = apellidos
                resultado['descripcion'] = descripcion or ''
                resultado['formato'] = formato or ''
                resultado['nombre_archivo'] = nombre_archivo or ''
                resultado['nombre_empleado'] = nombre_empleado
            elif len(empleado) >= 6:
                id_db, codigo_barras, id_unico, nombre_empleado, formato, nombre_archivo = empleado
                partes = nombre_empleado.strip().split()
                if len(partes) >= 2:
                    nombres = partes[0]
                    apellidos = " ".join(partes[1:])
                else:
                    nombres = nombre_empleado
                    apellidos = ''
                
                resultado['id_db'] = id_db
                resultado['codigo_barras'] = codigo_barras
                resultado['id_unico'] = id_unico
                resultado['nombres'] = nombres
                resultado['apellidos'] = apellidos
                resultado['descripcion'] = ''
                resultado['formato'] = formato or ''
                resultado['nombre_archivo'] = nombre_archivo or ''
                resultado['nombre_empleado'] = nombre_empleado
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error al desempaquetar empleado: {e}")
            return None
        
        return resultado
    
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
        emp = self._desempaquetar_empleado(empleado)
        if not emp:
            return
        
        codigo_path = IMAGES_DIR / emp['nombre_archivo']
        
        # Actualizar campos de variables dinámicamente
        if emp['nombre_empleado'] and "nombre" in self.controls_panel.campos_variables:
            campo_nombre = self.controls_panel.campos_variables["nombre"]
            if not isinstance(campo_nombre, dict):
                campo_nombre.setText(emp['nombre_empleado'])
        
        # Actualizar campos de nombres separados si existen
        if "nombres" in self.controls_panel.campos_variables:
            campo_nombres = self.controls_panel.campos_variables["nombres"]
            if not isinstance(campo_nombres, dict):
                campo_nombres.setText(emp['nombres'])
        
        if "apellidos" in self.controls_panel.campos_variables:
            campo_apellidos = self.controls_panel.campos_variables["apellidos"]
            if not isinstance(campo_apellidos, dict):
                campo_apellidos.setText(emp['apellidos'])
        
        # Actualizar ID único (automático)
        if "id_unico" in self.controls_panel.campos_variables:
            campo_id = self.controls_panel.campos_variables["id_unico"]
            if not isinstance(campo_id, dict):
                campo_id.setText(emp['id_unico'] or "")
        
        # Actualizar descripción si existe
        if "descripcion" in self.controls_panel.campos_variables:
            campo_desc = self.controls_panel.campos_variables["descripcion"]
            if not isinstance(campo_desc, dict):
                campo_desc.setText(emp['descripcion'] or "")
        
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
            emp = self._desempaquetar_empleado(self.empleado_actual)
            if not emp:
                return
            
            nombre = emp['nombre_empleado'] or "SIN NOMBRE"
            codigo_path = IMAGES_DIR / emp['nombre_archivo'] if emp['nombre_archivo'] else Path("")
            
            # ID único siempre se obtiene del empleado
            if "id_unico" in variables_template:
                variables["id_unico"] = emp['id_unico'] or ""
                # Actualizar campo en la UI si existe
                if "id_unico" in self.controls_panel.campos_variables:
                    campo_id = self.controls_panel.campos_variables["id_unico"]
                    if not isinstance(campo_id, dict):
                        campo_id.setText(emp['id_unico'] or "")
            
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
            
            # Nombres y apellidos separados (nuevas variables)
            if "nombres" in variables_template:
                variables["nombres"] = variables_usuario.get("nombres", emp['nombres']) or emp['nombres']
            
            if "apellidos" in variables_template:
                variables["apellidos"] = variables_usuario.get("apellidos", emp['apellidos']) or emp['apellidos']
            
            # Código de empleado (descripcion)
            if "descripcion" in variables_template:
                variables["descripcion"] = variables_usuario.get("descripcion", emp['descripcion']) or emp['descripcion']
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
            if "nombres" in variables_template:
                variables["nombres"] = variables_usuario.get("nombres", "JUAN") or "JUAN"
            if "apellidos" in variables_template:
                variables["apellidos"] = variables_usuario.get("apellidos", "PÉREZ") or "PÉREZ"
        
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
            emp = self._desempaquetar_empleado(self.empleado_actual)
            if not emp:
                nombre = "SIN NOMBRE"
                codigo_path = None
                return
            
            nombre = emp['nombre_empleado'] or "SIN NOMBRE"
            codigo_path = IMAGES_DIR / emp['nombre_archivo']
        
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
        
        # Desempaquetar para obtener datos del empleado
        emp = self._desempaquetar_empleado(empleado)
        if not emp:
            QMessageBox.warning(
                self.employees_panel,
                "Error",
                "Datos de empleado incompletos"
            )
            return
        
        # Pedir al usuario dónde guardar el PNG
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        from src.utils.file_utils import limpiar_nombre_archivo
        nombre_limpio = limpiar_nombre_archivo(emp['nombre_empleado'] or "sin_nombre")
        nombre_png_default = f"carnet_{nombre_limpio}_{emp['id_unico']}_{fecha_hora}.png"
        
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
        progress.set_cancelable(True)  # Habilitar botón cancelar
        progress.actualizar_progreso(0, 1, "Preparando generación...")
        progress.show()
        QApplication.processEvents()
        
        # Ruta del código de barras
        codigo_path = IMAGES_DIR / emp['nombre_archivo']
        if not codigo_path.exists():
            QMessageBox.warning(
                self.employees_panel,
                "Error",
                f"No se encontró la imagen del código de barras: {emp['nombre_archivo']}"
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
                nombre = emp['nombre_empleado'] or "SIN NOMBRE"
                if "id_unico" in variables_template:
                    variables["id_unico"] = emp['id_unico']
                if "codigo_barras" in variables_template:
                    variables["codigo_barras"] = codigo_path
                if "nombre" in variables_template:
                    variables["nombre"] = variables_usuario.get("nombre", nombre) or nombre
                if "nombres" in variables_template:
                    variables["nombres"] = variables_usuario.get("nombres", emp['nombres']) or emp['nombres']
                if "apellidos" in variables_template:
                    variables["apellidos"] = variables_usuario.get("apellidos", emp['apellidos']) or emp['apellidos']
                if "descripcion" in variables_template:
                    variables["descripcion"] = variables_usuario.get("descripcion", emp['descripcion']) or emp['descripcion']
                
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
                # Construir nombre completo para logging
                nombre_completo = nombre if nombre else (f"{emp.get('nombres', '')} {emp.get('apellidos', '')}".strip() or "SIN NOMBRE")
                logger.info(f"Renderizando carnet HTML para {nombre_completo}")
                logger.info(f"Variables inyectadas: {list(variables.keys())}")
                logger.info(f"Tamaño del HTML: {len(html_content)} caracteres")
                
                # Sistema de reintentos robusto para evitar imágenes en blanco
                max_reintentos = 5
                imagen = None
                
                for intento in range(1, max_reintentos + 1):
                    progress.actualizar_progreso(0, max_reintentos, f"Renderizando carnet (intento {intento}/{max_reintentos})...")
                    QApplication.processEvents()
                    
                    # Asegurar que el widget esté completamente inicializado antes del primer renderizado
                    if not self.html_renderer._inicializado:
                        logger.info("Inicializando widget HTML...")
                        from PyQt6.QtCore import QTimer
                        QTimer.singleShot(500, lambda: None)
                        QApplication.processEvents()
                    
                    # Esperar antes de renderizar (más tiempo en los primeros intentos)
                    if intento > 1:
                        tiempo_espera = 1500 if intento == 2 else (1000 if intento == 3 else 800)
                        from PyQt6.QtCore import QTimer
                        QTimer.singleShot(tiempo_espera, lambda: None)
                        QApplication.processEvents()
                    
                    # Renderizar HTML a imagen con alta calidad (600 DPI)
                    imagen = self.html_renderer.renderizar_html_a_imagen(
                        html_content=html_content,
                        ancho=html_template.ancho,
                        alto=html_template.alto,
                        dpi=600  # Alta calidad para impresión profesional
                    )
                    
                    if not imagen:
                        logger.warning(f"Intento {intento}: No se generó imagen")
                        if intento < max_reintentos:
                            continue
                        else:
                            break
                    
                    # Verificar que la imagen no esté completamente en blanco
                    ancho_img, alto_img = imagen.size
                    if ancho_img > 100 and alto_img > 100:
                        from PIL import ImageStat
                        stat = ImageStat.Stat(imagen)
                        if len(stat.mean) >= 3:
                            media_r, media_g, media_b = stat.mean[0], stat.mean[1], stat.mean[2]
                            # Si la media es muy cercana a 255 en todos los canales, está en blanco
                            if media_r > 250 and media_g > 250 and media_b > 250:
                                logger.warning(f"Intento {intento}: Imagen en blanco detectada (R:{media_r:.1f}, G:{media_g:.1f}, B:{media_b:.1f})")
                                if intento < max_reintentos:
                                    progress.actualizar_progreso(intento, max_reintentos, f"Imagen en blanco detectada, reintentando ({intento}/{max_reintentos})...")
                                    QApplication.processEvents()
                                    imagen = None  # Marcar para reintentar
                                    continue
                                else:
                                    logger.error("Imagen en blanco después de todos los intentos")
                                    break
                    
                    # Si llegamos aquí, la imagen es válida
                    logger.info(f"✓ Imagen renderizada correctamente en intento {intento}: {imagen.size}")
                    break
                
                if not imagen:
                    progress.close()
                    QMessageBox.warning(
                        self.employees_panel,
                        "Error",
                        f"No se pudo renderizar el carnet después de {max_reintentos} intentos.\n\n"
                        "Intente generar nuevamente o verifique el template HTML."
                    )
                    return
                
                progress.actualizar_progreso(0, 1, "Guardando carnet...")
                QApplication.processEvents()
                
                # Guardar carnet con máxima calidad PNG en la ubicación elegida por el usuario
                # Guardar con máxima calidad (600 DPI, sin optimización, compresión mínima)
                imagen.save(ruta_png_path, "PNG", dpi=(600, 600), optimize=False, compress_level=1)
                
                # Verificar cancelación antes de verificar con OCR
                if progress.fue_cancelado():
                    logger.info("Generación individual PNG cancelada antes de verificar con OCR")
                    progress.close()
                    return
                
                # Verificar con OCR si está disponible
                mensaje_verificacion = ""
                if self.usar_ocr and self.ocr_verifier:
                    import logging
                    logger_ocr = logging.getLogger(__name__)
                    progress.actualizar_progreso(0, 1, "Verificando con OCR...")
                    QApplication.processEvents()
                    
                    # Verificar cancelación antes de verificar OCR
                    if progress.fue_cancelado():
                        logger.info("Generación individual PNG cancelada durante verificación OCR")
                        progress.close()
                        return
                    
                    # Preparar datos esperados para OCR
                    datos_esperados = {}
                    if emp.get('nombres'):
                        datos_esperados['nombres'] = emp['nombres']
                    if emp.get('apellidos'):
                        datos_esperados['apellidos'] = emp['apellidos']
                    if emp.get('descripcion'):
                        datos_esperados['descripcion'] = emp['descripcion']
                    if emp.get('id_unico'):
                        datos_esperados['id_unico'] = emp['id_unico']
                    
                    # Verificar con OCR
                    exito_ocr, mensaje_ocr, detalles = self.ocr_verifier.verificar_carnet(
                        ruta_png_path,
                        datos_esperados,
                        umbral_similitud=0.65
                    )
                    
                    if exito_ocr:
                        mensaje_verificacion = f"\n\n✓ Verificación OCR: {mensaje_ocr}"
                        logger_ocr.info(f"✓ Carnet PNG verificado correctamente con OCR")
                    else:
                        mensaje_verificacion = f"\n\n⚠ Verificación OCR: {mensaje_ocr}"
                        logger_ocr.warning(f"⚠ Verificación OCR falló: {mensaje_ocr}")
                
                progress.actualizar_progreso(1, 1, "¡Carnet generado exitosamente!")
                QApplication.processEvents()
                progress.marcar_completado()  # Marcar como completado antes de cerrar
                progress.close()
                
                mensaje_final = f"Carnet PNG generado exitosamente:\n{ruta_png_path}{mensaje_verificacion}"
                QMessageBox.information(
                    self.employees_panel,
                    "Éxito",
                    mensaje_final
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
                    nombre_empleado=emp['nombre_empleado'] or "SIN NOMBRE",
                    codigo_barras_path=str(codigo_path),
                    empresa=template.empresa_texto if template.mostrar_empresa else None,
                    web=template.web_texto if template.mostrar_web else None
                )
                
                progress.actualizar_progreso(0, 1, "Guardando carnet...")
                QApplication.processEvents()
                
                # Guardar carnet en la ubicación elegida por el usuario
                if self.designer.guardar_carnet(imagen, ruta_png_path):
                    # Verificar con OCR si está disponible
                    mensaje_verificacion = ""
                    if self.usar_ocr and self.ocr_verifier:
                        import logging
                        logger_ocr = logging.getLogger(__name__)
                        progress.actualizar_progreso(0, 1, "Verificando con OCR...")
                        QApplication.processEvents()
                        
                        # Preparar datos esperados para OCR
                        datos_esperados = {}
                        if emp.get('nombres'):
                            datos_esperados['nombres'] = emp['nombres']
                        if emp.get('apellidos'):
                            datos_esperados['apellidos'] = emp['apellidos']
                        if emp.get('descripcion'):
                            datos_esperados['descripcion'] = emp['descripcion']
                        if emp.get('id_unico'):
                            datos_esperados['id_unico'] = emp['id_unico']
                        
                        # Verificar con OCR
                        exito_ocr, mensaje_ocr, detalles = self.ocr_verifier.verificar_carnet(
                            ruta_png_path,
                            datos_esperados,
                            umbral_similitud=0.65
                        )
                        
                        if exito_ocr:
                            mensaje_verificacion = f"\n\n✓ Verificación OCR: {mensaje_ocr}"
                            logger_ocr.info(f"✓ Carnet PNG verificado correctamente con OCR")
                        else:
                            mensaje_verificacion = f"\n\n⚠ Verificación OCR: {mensaje_ocr}"
                            logger_ocr.warning(f"⚠ Verificación OCR falló: {mensaje_ocr}")
                    
                    progress.actualizar_progreso(1, 1, "¡Carnet generado exitosamente!")
                    QApplication.processEvents()
                    progress.close()
                    
                    mensaje_final = f"Carnet PNG generado exitosamente:\n{ruta_png_path}{mensaje_verificacion}"
                    QMessageBox.information(
                        self.employees_panel,
                        "Éxito",
                        mensaje_final
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
    
    def _generar_carnet_con_verificacion_ocr(
        self,
        funcion_generacion: callable,
        empleado_datos: dict,
        ruta_salida: Path,
        verificar_ocr: bool = True,
        max_reintentos: int = 3,
        callback_progreso: Optional[callable] = None,
        progress_dialog: Optional[object] = None
    ) -> tuple[bool, str, Optional[Path]]:
        """
        Genera un carnet y verifica con OCR que se generó correctamente.
        
        Args:
            funcion_generacion: Función que genera el carnet y retorna PIL.Image
            empleado_datos: Diccionario con datos del empleado (nombres, apellidos, etc.)
            ruta_salida: Path donde guardar el carnet
            verificar_ocr: Si True, verifica con OCR (default: True)
            max_reintentos: Número máximo de intentos (default: 3)
        
        Returns:
            Tupla (exito, mensaje, ruta_imagen)
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Si OCR no está disponible o no se quiere verificar, simplemente generar
        if not verificar_ocr or not self.usar_ocr or not self.ocr_verifier:
            try:
                imagen = funcion_generacion()
                if imagen:
                    imagen.save(ruta_salida, "PNG", dpi=(600, 600), optimize=False, compress_level=1)
                    return True, "Carnet generado exitosamente (sin verificación OCR)", ruta_salida
                else:
                    return False, "Error al generar carnet", None
            except Exception as e:
                return False, f"Error al generar carnet: {str(e)}", None
        
        # Generar con verificación OCR
        for intento in range(1, max_reintentos + 1):
            # Verificar cancelación antes de cada intento
            if progress_dialog and hasattr(progress_dialog, 'fue_cancelado') and progress_dialog.fue_cancelado():
                logger.info("Generación cancelada por el usuario durante verificación OCR")
                return False, "Generación cancelada por el usuario", None
            
            try:
                logger.info(f"Generando carnet (intento {intento}/{max_reintentos})...")
                logger.info(f"Datos del empleado: nombres={empleado_datos.get('nombres')}, apellidos={empleado_datos.get('apellidos')}, descripcion={empleado_datos.get('descripcion')}, id_unico={empleado_datos.get('id_unico')}")
                
                if callback_progreso:
                    callback_progreso(f"Generando carnet (intento {intento}/{max_reintentos})...")
                
                # Verificar cancelación antes de generar
                if progress_dialog and hasattr(progress_dialog, 'fue_cancelado') and progress_dialog.fue_cancelado():
                    logger.info("Generación cancelada por el usuario antes de generar imagen")
                    return False, "Generación cancelada por el usuario", None
                
                # Generar imagen
                imagen = funcion_generacion()
                
                # Verificar cancelación después de generar
                if progress_dialog and hasattr(progress_dialog, 'fue_cancelado') and progress_dialog.fue_cancelado():
                    logger.info("Generación cancelada por el usuario después de generar imagen")
                    return False, "Generación cancelada por el usuario", None
                
                if not imagen:
                    logger.warning(f"Intento {intento}: Generación falló, no se creó la imagen")
                    if intento < max_reintentos:
                        import time
                        time.sleep(0.3)
                    continue
                
                # Guardar imagen temporal para verificación
                imagen.save(ruta_salida, "PNG", dpi=(600, 600), optimize=False, compress_level=1)
                
                # Preparar datos esperados para OCR
                datos_esperados = {}
                if empleado_datos.get('nombres'):
                    datos_esperados['nombres'] = empleado_datos['nombres']
                if empleado_datos.get('apellidos'):
                    datos_esperados['apellidos'] = empleado_datos['apellidos']
                if empleado_datos.get('descripcion'):
                    datos_esperados['descripcion'] = empleado_datos['descripcion']
                if empleado_datos.get('id_unico'):
                    datos_esperados['id_unico'] = empleado_datos['id_unico']
                
                logger.info(f"Datos esperados para OCR: {datos_esperados}")
                
                # Verificar con OCR
                if callback_progreso:
                    callback_progreso(f"Verificando con OCR (intento {intento}/{max_reintentos})...")
                logger.info(f"Verificando carnet con OCR (intento {intento})...")
                exito_ocr, mensaje_ocr, detalles = self.ocr_verifier.verificar_carnet(
                    ruta_salida,
                    datos_esperados,
                    umbral_similitud=0.65  # Umbral más bajo para tolerar errores menores de OCR
                )
                
                if exito_ocr:
                    logger.info(f"✓ Carnet verificado correctamente en intento {intento}")
                    if callback_progreso:
                        callback_progreso(f"✓ Verificado correctamente")
                    return True, f"Carnet generado y verificado: {mensaje_ocr}", ruta_salida
                else:
                    logger.warning(f"✗ Intento {intento} falló verificación: {mensaje_ocr}")
                    logger.warning(f"Detalles de verificación: {detalles}")
                    if callback_progreso:
                        callback_progreso(f"✗ Verificación falló: {mensaje_ocr}. Reintentando...")
                    if intento < max_reintentos:
                        logger.info("Reintentando generación...")
                        import time
                        time.sleep(0.5)
                        # Limpiar imagen anterior
                        if ruta_salida.exists():
                            try:
                                ruta_salida.unlink()
                            except:
                                pass
            
            except Exception as e:
                logger.error(f"Error en intento {intento}: {e}", exc_info=True)
                if intento >= max_reintentos:
                    # En el último intento, guardar lo que tengamos
                    try:
                        if 'imagen' in locals() and imagen:
                            imagen.save(ruta_salida, "PNG", dpi=(600, 600), optimize=False, compress_level=1)
                            return True, f"Carnet generado (verificación OCR incompleta: {str(e)})", ruta_salida
                    except:
                        pass
                    return False, f"Error tras {max_reintentos} intentos: {str(e)}", None
        
        # Si llegamos aquí, fallaron todos los intentos de verificación
        # Pero guardamos el último intento de todas formas
        mensaje = f"Carnet generado pero no se pudo verificar completamente con OCR tras {max_reintentos} intentos"
        logger.warning(mensaje)
        return True, mensaje, ruta_salida
    
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
        progress.set_cancelable(True)  # Habilitar botón cancelar
        progress.show()
        QApplication.processEvents()
        
        exitosos = 0
        errores = 0
        total = len(empleados)
        errores_ocr = 0  # Contador de errores de OCR
        ocr_usado_exitosamente = False  # Flag para saber si OCR funcionó al menos una vez
        
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
                # Verificar si se canceló
                if progress.fue_cancelado():
                    logger.info("Generación masiva cancelada por el usuario")
                    break
                
                # Actualizar progreso
                nombre_empleado_temp = ""
                try:
                    if len(empleado) >= 5:
                        nombre_empleado_temp = empleado[4] if len(empleado) >= 5 else "empleado"
                except:
                    nombre_empleado_temp = "empleado"
                
                faltantes = total - indice + 1
                estado_ocr = "✓ Con verificación OCR" if self.usar_ocr else "⚠ Sin verificación OCR (no disponible)"
                progress.actualizar_progreso(
                    indice - 1, 
                    total, 
                    f"Generando carnet {indice} de {total}\nFaltan {faltantes} carnet(s) por generar\n{estado_ocr}\nEmpleado: {nombre_empleado_temp}"
                )
                QApplication.processEvents()
                
                # Verificar cancelación después de actualizar UI
                if progress.fue_cancelado():
                    logger.info("Generación masiva cancelada por el usuario")
                    break
                try:
                    # Desempaquetar usando función auxiliar
                    emp = self._desempaquetar_empleado(empleado)
                    if not emp:
                        errores += 1
                        continue
                    
                    codigo_path = IMAGES_DIR / emp['nombre_archivo']
                    if not codigo_path.exists():
                        errores += 1
                        continue
                    
                    if usar_html:
                        # Usar renderizado HTML
                        variables = {}
                        
                        # Datos del empleado - EN GENERACIÓN MASIVA USAR SOLO DATOS DEL EMPLEADO, NO DE PANTALLA
                        # IMPORTANTE: Usar directamente los datos del empleado actual, NO los de la pantalla
                        nombre = emp['nombre_empleado'] or "SIN NOMBRE"
                        if "id_unico" in variables_template:
                            variables["id_unico"] = emp['id_unico'] or ""
                        if "codigo_barras" in variables_template:
                            variables["codigo_barras"] = codigo_path
                        if "nombre" in variables_template:
                            variables["nombre"] = nombre
                        if "nombres" in variables_template:
                            # FORZAR uso del nombre del empleado actual, no de pantalla
                            variables["nombres"] = emp.get('nombres') or ""
                        if "apellidos" in variables_template:
                            # FORZAR uso del apellido del empleado actual, no de pantalla
                            variables["apellidos"] = emp.get('apellidos') or ""
                        if "descripcion" in variables_template:
                            variables["descripcion"] = emp.get('descripcion') or ""
                        
                        # Logo y foto - ESTOS SÍ vienen de pantalla (son globales)
                        if "logo" in variables_template:
                            logo_path = variables_usuario.get("logo")
                            if logo_path and isinstance(logo_path, Path) and logo_path.exists():
                                variables["logo"] = logo_path
                            else:
                                variables["logo"] = Path("")
                        if "foto" in variables_template:
                            variables["foto"] = Path("")
                        
                        # Otras variables globales (empresa, web, cargo, etc.) - NO los datos del empleado
                        for var in variables_template:
                            if var not in {"id_unico", "codigo_barras", "foto", "logo", "nombre", "nombres", "apellidos", "descripcion"}:
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
                        
                        # Logging para debug
                        import logging
                        logger_debug = logging.getLogger(__name__)
                        logger_debug.info(f"=== Generando carnet para empleado {indice}/{total} ===")
                        logger_debug.info(f"Emp datos: nombres={emp.get('nombres')}, apellidos={emp.get('apellidos')}, descripcion={emp.get('descripcion')}, id_unico={emp.get('id_unico')}")
                        logger_debug.info(f"Variables antes de inyectar: nombres={variables.get('nombres')}, apellidos={variables.get('apellidos')}, descripcion={variables.get('descripcion')}")
                        
                        # Inyectar variables en HTML
                        html_content = self.html_renderer._inyectar_variables(html_base, variables)
                        
                        # Preparar nombre y ruta del carnet
                        from src.utils.file_utils import limpiar_nombre_archivo
                        nombre_limpio = limpiar_nombre_archivo(emp['nombre_empleado'] or "sin_nombre")
                        nombre_archivo_carnet = f"carnet_{nombre_limpio}_{emp['id_unico']}.png"
                        ruta_carnet = directorio_temp / nombre_archivo_carnet
                        
                        # Función para generar el carnet (captura html_content del scope actual)
                        html_content_actual = html_content  # Capturar en variable local
                        def generar_carnet_html():
                            return self.html_renderer.renderizar_html_a_imagen(
                                html_content=html_content_actual,
                            ancho=html_template.ancho,
                            alto=html_template.alto,
                                dpi=600
                            )
                        
                        # Callback para actualizar progreso
                        def actualizar_progreso_ocr(mensaje):
                            progress.actualizar_progreso(
                                indice - 1,
                                total,
                                f"Generando carnet {indice} de {total}\n{mensaje}\nEmpleado: {emp.get('nombres', '')} {emp.get('apellidos', '')}"
                            )
                            QApplication.processEvents()
                        
                        # Generar con verificación OCR (solo si está disponible)
                        exito, mensaje_ocr, ruta_final = self._generar_carnet_con_verificacion_ocr(
                            generar_carnet_html,
                            emp,
                            ruta_carnet,
                            verificar_ocr=self.usar_ocr,  # Solo verificar si OCR está disponible
                            max_reintentos=2,  # Solo 2 reintentos en masivo para no hacerlo muy lento
                            callback_progreso=actualizar_progreso_ocr if self.usar_ocr else None
                        )
                        
                        logger_debug.info(f"Resultado: exito={exito}, mensaje={mensaje_ocr}")
                        
                        # Rastrear estado de OCR
                        if self.usar_ocr:
                            if "verificado" in mensaje_ocr.lower() or "verificación" in mensaje_ocr.lower():
                                if "incompleta" not in mensaje_ocr.lower() and "error" not in mensaje_ocr.lower():
                                    ocr_usado_exitosamente = True
                                else:
                                    errores_ocr += 1
                            elif "error" in mensaje_ocr.lower() or "no disponible" in mensaje_ocr.lower():
                                errores_ocr += 1
                        
                        if exito and ruta_final:
                            archivos_generados.append(ruta_final)
                            exitosos += 1
                        else:
                            errores += 1
                    else:
                        # Usar sistema PIL antiguo
                        import logging
                        logger_debug = logging.getLogger(__name__)
                        logger_debug.info(f"=== Generando carnet PIL para empleado {indice}/{total} ===")
                        logger_debug.info(f"Emp datos: nombres={emp.get('nombres')}, apellidos={emp.get('apellidos')}, descripcion={emp.get('descripcion')}, id_unico={emp.get('id_unico')}")
                        
                        from src.utils.file_utils import limpiar_nombre_archivo
                        nombre_limpio = limpiar_nombre_archivo(emp['nombre_empleado'] or "sin_nombre")
                        nombre_archivo_carnet = f"carnet_{nombre_limpio}_{emp['id_unico']}.png"
                        ruta_carnet = directorio_temp / nombre_archivo_carnet
                        
                        # Función para generar el carnet
                        def generar_carnet_pil():
                            return self.designer.renderizar_carnet(
                            template=template,
                                nombre_empleado=emp['nombre_empleado'] or "SIN NOMBRE",
                            codigo_barras_path=str(codigo_path),
                            empresa=template.empresa_texto if template.mostrar_empresa else None,
                            web=template.web_texto if template.mostrar_web else None
                        )
                        
                        # Callback para actualizar progreso
                        def actualizar_progreso_ocr(mensaje):
                            progress.actualizar_progreso(
                                indice - 1,
                                total,
                                f"Generando carnet {indice} de {total}\n{mensaje}\nEmpleado: {emp.get('nombres', '')} {emp.get('apellidos', '')}"
                            )
                            QApplication.processEvents()
                        
                        # Verificar cancelación antes de generar
                        if progress.fue_cancelado():
                            logger.info("Generación cancelada antes de generar carnet PIL")
                            break
                        
                        # Generar con verificación OCR
                        exito, mensaje_ocr, ruta_final = self._generar_carnet_con_verificacion_ocr(
                            generar_carnet_pil,
                            emp,
                            ruta_carnet,
                            verificar_ocr=self.usar_ocr,
                            max_reintentos=2,
                            callback_progreso=actualizar_progreso_ocr if self.usar_ocr else None,
                            progress_dialog=progress  # Pasar el diálogo para verificar cancelación
                        )
                        
                        # Verificar cancelación después de generar
                        if progress.fue_cancelado():
                            logger.info("Generación cancelada después de generar carnet PIL")
                            break
                        
                        logger_debug.info(f"Resultado PIL: exito={exito}, mensaje={mensaje_ocr}")
                        
                        # Rastrear estado de OCR
                        if self.usar_ocr:
                            if "verificado" in mensaje_ocr.lower() or "verificación" in mensaje_ocr.lower():
                                if "incompleta" not in mensaje_ocr.lower() and "error" not in mensaje_ocr.lower():
                                    ocr_usado_exitosamente = True
                                else:
                                    errores_ocr += 1
                            elif "error" in mensaje_ocr.lower() or "no disponible" in mensaje_ocr.lower():
                                errores_ocr += 1
                        
                        if exito and ruta_final:
                            archivos_generados.append(ruta_final)
                            exitosos += 1
                        else:
                            errores += 1
                except Exception as e:
                    errores += 1
                    import logging
                    logger = logging.getLogger(__name__)
                    # Intentar obtener nombre del empleado para el log
                    try:
                        emp_error = self._desempaquetar_empleado(empleado)
                        nombre_error = emp_error['nombre_empleado'] if emp_error else "desconocido"
                    except:
                        nombre_error = "desconocido"
                    logger.error(f"Error al generar carnet para {nombre_error}: {e}")
            
            # Verificar si se canceló antes de comprimir
            if progress.fue_cancelado():
                logger.info("Generación cancelada antes de comprimir ZIP")
                if directorio_temp and directorio_temp.exists():
                    import shutil
                    try:
                        shutil.rmtree(directorio_temp)
                    except:
                        pass
                progress.close()
                QMessageBox.information(
                    self.employees_panel,
                    "Generación Cancelada",
                    f"Generación cancelada por el usuario.\n\n"
                    f"Carnets generados hasta el momento: {exitosos}\n"
                    f"Errores: {errores}"
                )
                return
            
            # Crear archivo ZIP con todos los carnets generados
            if archivos_generados:
                progress.actualizar_progreso(total, total + 1, "Comprimiendo carnets en ZIP...")
                QApplication.processEvents()
                
                # Verificar cancelación antes de comprimir
                if progress.fue_cancelado():
                    logger.info("Generación cancelada antes de comprimir ZIP")
                    if directorio_temp and directorio_temp.exists():
                        import shutil
                        try:
                            shutil.rmtree(directorio_temp)
                        except:
                            pass
                    progress.close()
                    QMessageBox.information(
                        self.employees_panel,
                        "Generación Cancelada",
                        f"Generación cancelada por el usuario.\n\n"
                        f"Carnets generados hasta el momento: {exitosos}\n"
                        f"Errores: {errores}"
                    )
                    return
                
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
        progress.marcar_completado()  # Marcar como completado antes de cerrar
        progress.close()
        
        mensaje = f"Generación completada:\n{exitosos} carnet(s) generado(s) y guardado(s) en:\n{ruta_zip_path}"
        
        # Mensaje de OCR basado en el estado real
        if self.usar_ocr:
            if ocr_usado_exitosamente and errores_ocr == 0:
                mensaje += f"\n\n✓ Verificación OCR: Habilitada (todos los carnets fueron verificados)"
            elif ocr_usado_exitosamente and errores_ocr > 0:
                mensaje += f"\n\n⚠ Verificación OCR: Parcial (algunos carnets no pudieron ser verificados: {errores_ocr} error(es))"
            else:
                mensaje += f"\n\n⚠ Verificación OCR: No disponible (Tesseract no está instalado o no está en PATH)"
        else:
            mensaje += f"\n\n⚠ Verificación OCR: No disponible (Tesseract no está instalado)"
        
        if errores > 0:
            mensaje += f"\n\n{errores} error(es) durante la generación"
        
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
        emp = self._desempaquetar_empleado(empleado)
        if not emp:
            progress.close()
            QMessageBox.warning(
                self.employees_panel,
                "Error",
                "Datos de empleado incompletos"
            )
            return
        
        codigo_path = IMAGES_DIR / emp['nombre_archivo']
        if not codigo_path.exists():
            progress.close()
            QMessageBox.warning(
                self.employees_panel,
                "Error",
                f"No se encontró la imagen del código de barras: {emp['nombre_archivo']}"
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
                
                nombre = emp['nombre_empleado'] or "SIN NOMBRE"
                if "id_unico" in variables_template:
                    variables["id_unico"] = emp['id_unico']
                if "codigo_barras" in variables_template:
                    variables["codigo_barras"] = codigo_path
                if "nombre" in variables_template:
                    variables["nombre"] = variables_usuario.get("nombre", nombre) or nombre
                if "nombres" in variables_template:
                    variables["nombres"] = variables_usuario.get("nombres", emp['nombres']) or emp['nombres']
                if "apellidos" in variables_template:
                    variables["apellidos"] = variables_usuario.get("apellidos", emp['apellidos']) or emp['apellidos']
                if "descripcion" in variables_template:
                    variables["descripcion"] = variables_usuario.get("descripcion", emp['descripcion']) or emp['descripcion']
                
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
                
                # Sistema de reintentos robusto para evitar imágenes en blanco
                import logging
                logger_pdf = logging.getLogger(__name__)
                max_reintentos = 5
                imagen = None
                
                for intento in range(1, max_reintentos + 1):
                    # Verificar cancelación antes de cada intento
                    if progress.fue_cancelado():
                        logger_pdf.info("Generación individual PDF cancelada por el usuario")
                        progress.close()
                        return
                    
                    progress.actualizar_progreso(0, max_reintentos, f"Renderizando carnet PDF (intento {intento}/{max_reintentos})...")
                    QApplication.processEvents()
                    
                    # Verificar cancelación después de actualizar UI
                    if progress.fue_cancelado():
                        logger_pdf.info("Generación individual PDF cancelada por el usuario")
                        progress.close()
                        return
                    
                    # Asegurar que el widget esté completamente inicializado
                    if not self.html_renderer._inicializado:
                        logger_pdf.info("Inicializando widget HTML...")
                        from PyQt6.QtCore import QTimer
                        QTimer.singleShot(500, lambda: None)
                        QApplication.processEvents()
                    
                    # Esperar antes de renderizar (más tiempo en los primeros intentos)
                    if intento > 1:
                        tiempo_espera = 1500 if intento == 2 else (1000 if intento == 3 else 800)
                        from PyQt6.QtCore import QTimer
                        QTimer.singleShot(tiempo_espera, lambda: None)
                        QApplication.processEvents()
                    
                    # Renderizar a máxima calidad (1200 DPI para PDF de super mega calidad)
                    imagen = self.html_renderer.renderizar_html_a_imagen(
                        html_content=html_content,
                        ancho=html_template.ancho,
                        alto=html_template.alto,
                        dpi=1200  # Super mega calidad para PDF
                    )
                    
                    if not imagen:
                        logger_pdf.warning(f"Intento {intento}: No se generó imagen")
                        if intento < max_reintentos:
                            continue
                        else:
                            break
                    
                    # Verificar que la imagen no esté completamente en blanco
                    ancho_img, alto_img = imagen.size
                    if ancho_img > 100 and alto_img > 100:
                        from PIL import ImageStat
                        stat = ImageStat.Stat(imagen)
                        if len(stat.mean) >= 3:
                            media_r, media_g, media_b = stat.mean[0], stat.mean[1], stat.mean[2]
                            # Si la media es muy cercana a 255 en todos los canales, está en blanco
                            if media_r > 250 and media_g > 250 and media_b > 250:
                                logger_pdf.warning(f"Intento {intento}: Imagen en blanco detectada (R:{media_r:.1f}, G:{media_g:.1f}, B:{media_b:.1f})")
                                if intento < max_reintentos:
                                    progress.actualizar_progreso(intento, max_reintentos, f"Imagen en blanco detectada, reintentando ({intento}/{max_reintentos})...")
                                    QApplication.processEvents()
                                    imagen = None  # Marcar para reintentar
                                    continue
                                else:
                                    logger_pdf.error("Imagen en blanco después de todos los intentos")
                                    break
                    
                    # Si llegamos aquí, la imagen es válida
                    logger_pdf.info(f"✓ Imagen renderizada correctamente en intento {intento}: {imagen.size}")
                    break
                
                if not imagen:
                    progress.close()
                    QMessageBox.warning(
                        self.employees_panel,
                        "Error",
                        f"No se pudo renderizar el carnet PDF después de {max_reintentos} intentos.\n\n"
                        "Intente generar nuevamente o verifique el template HTML."
                    )
                    return
            else:
                # Usar sistema PIL
                template = self.controls_panel.obtener_template_actualizado()
                progress.actualizar_progreso(0, 1, "Renderizando carnet...")
                QApplication.processEvents()
                
                imagen = self.designer.renderizar_carnet(
                    template=template,
                    nombre_empleado=emp['nombre_empleado'] or "SIN NOMBRE",
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
            
            # Verificar cancelación antes de verificar con OCR
            if progress.fue_cancelado():
                logger.info("Generación individual PDF cancelada antes de verificar con OCR")
                progress.close()
                return
            
            # Verificar con OCR si está disponible
            mensaje_verificacion = ""
            if self.usar_ocr and self.ocr_verifier:
                import logging
                logger_ocr = logging.getLogger(__name__)
                progress.actualizar_progreso(0, 1, "Verificando con OCR...")
                QApplication.processEvents()
                
                # Verificar cancelación antes de verificar OCR
                if progress.fue_cancelado():
                    logger.info("Generación individual PDF cancelada durante verificación OCR")
                    progress.close()
                    return
                
                # Preparar datos esperados para OCR
                datos_esperados = {}
                if emp.get('nombres'):
                    datos_esperados['nombres'] = emp['nombres']
                if emp.get('apellidos'):
                    datos_esperados['apellidos'] = emp['apellidos']
                if emp.get('descripcion'):
                    datos_esperados['descripcion'] = emp['descripcion']
                if emp.get('id_unico'):
                    datos_esperados['id_unico'] = emp['id_unico']
                
                # Verificar con OCR
                exito_ocr, mensaje_ocr, detalles = self.ocr_verifier.verificar_carnet(
                    ruta_pdf_path,
                    datos_esperados,
                    umbral_similitud=0.65
                )
                
                if exito_ocr:
                    mensaje_verificacion = f"\n\n✓ Verificación OCR: {mensaje_ocr}"
                    logger_ocr.info(f"✓ Carnet PDF verificado correctamente con OCR")
                else:
                    mensaje_verificacion = f"\n\n⚠ Verificación OCR: {mensaje_ocr}"
                    logger_ocr.warning(f"⚠ Verificación OCR falló: {mensaje_ocr}")
            
            progress.actualizar_progreso(1, 1, "¡PDF generado exitosamente!")
            QApplication.processEvents()
            progress.marcar_completado()  # Marcar como completado antes de cerrar
            progress.close()
            
            mensaje_final = f"Carnet PDF generado exitosamente:\n{ruta_pdf_path}{mensaje_verificacion}"
            QMessageBox.information(
                self.employees_panel,
                "Éxito",
                mensaje_final
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
        import logging
        logger = logging.getLogger(__name__)
        
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
        progress.set_cancelable(True)  # Habilitar botón cancelar
        progress.show()
        QApplication.processEvents()
        
        exitosos = 0
        errores = 0
        total = len(empleados)
        errores_ocr = 0  # Contador de errores de OCR
        ocr_usado_exitosamente = False  # Flag para saber si OCR funcionó al menos una vez
        
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
                # Verificar si se canceló
                if progress.fue_cancelado():
                    logger.info("Generación masiva PDF cancelada por el usuario")
                    break
                
                nombre_empleado_temp = ""
                try:
                    if len(empleado) >= 5:
                        nombre_empleado_temp = empleado[4] if len(empleado) >= 5 else "empleado"
                except:
                    nombre_empleado_temp = "empleado"
                
                faltantes = total - indice + 1
                estado_ocr = "✓ Con verificación OCR" if self.usar_ocr else "⚠ Sin verificación OCR (no disponible)"
                progress.actualizar_progreso(
                    indice - 1,
                    total,
                    f"Generando PDF {indice} de {total}\nFaltan {faltantes} PDF(s) por generar\n{estado_ocr}\nEmpleado: {nombre_empleado_temp}"
                )
                QApplication.processEvents()
                
                # Verificar cancelación después de actualizar UI
                if progress.fue_cancelado():
                    logger.info("Generación masiva PDF cancelada por el usuario")
                    break
                
                try:
                    # Desempaquetar datos usando función auxiliar
                    emp = self._desempaquetar_empleado(empleado)
                    if not emp:
                        errores += 1
                        continue
                    
                    codigo_path = IMAGES_DIR / emp['nombre_archivo']
                    if not codigo_path.exists():
                        errores += 1
                        continue
                    
                    # Generar nombre del PDF en directorio temporal
                    from src.utils.file_utils import limpiar_nombre_archivo
                    nombre_limpio = limpiar_nombre_archivo(emp['nombre_empleado'] or "sin_nombre")
                    nombre_pdf = f"carnet_{nombre_limpio}_{emp['id_unico']}.pdf"
                    ruta_pdf = directorio_temp / nombre_pdf
                    
                    if usar_html:
                        # Preparar variables
                        # IMPORTANTE: Usar directamente los datos del empleado actual, NO los de la pantalla
                        variables = {}
                        nombre = emp['nombre_empleado'] or "SIN NOMBRE"
                        if "id_unico" in variables_template:
                            variables["id_unico"] = emp['id_unico'] or ""
                        if "codigo_barras" in variables_template:
                            variables["codigo_barras"] = codigo_path
                        if "nombre" in variables_template:
                            variables["nombre"] = nombre
                        if "nombres" in variables_template:
                            # FORZAR uso del nombre del empleado actual, no de pantalla
                            variables["nombres"] = emp.get('nombres') or ""
                        if "apellidos" in variables_template:
                            # FORZAR uso del apellido del empleado actual, no de pantalla
                            variables["apellidos"] = emp.get('apellidos') or ""
                        if "descripcion" in variables_template:
                            variables["descripcion"] = emp.get('descripcion') or ""
                        
                        # Logo y foto
                        if "logo" in variables_template:
                            logo_path = variables_usuario.get("logo")
                            if logo_path and isinstance(logo_path, Path) and logo_path.exists():
                                variables["logo"] = logo_path
                            else:
                                variables["logo"] = Path("")
                        if "foto" in variables_template:
                            variables["foto"] = Path("")
                        
                        # Otras variables globales
                        for var in variables_template:
                            if var not in {"id_unico", "codigo_barras", "foto", "logo", "nombre", "nombres", "apellidos", "descripcion"}:
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
                        
                        # Función para generar el carnet
                        def generar_carnet_html():
                            return self.html_renderer.renderizar_html_a_imagen(
                            html_content=html_content,
                            ancho=html_template.ancho,
                            alto=html_template.alto,
                                dpi=1200
                            )
                        
                        # Verificar cancelación antes de generar
                        if progress.fue_cancelado():
                            logger.info("Generación cancelada antes de generar carnet PDF HTML")
                            break
                        
                        # Generar PNG temporal para verificación OCR
                        ruta_png_temp = ruta_pdf.with_suffix('.png')
                        exito, mensaje_ocr, ruta_png_final = self._generar_carnet_con_verificacion_ocr(
                            generar_carnet_html,
                            emp,
                            ruta_png_temp,
                            verificar_ocr=self.usar_ocr,
                            max_reintentos=2,
                            progress_dialog=progress  # Pasar el diálogo para verificar cancelación
                        )
                        
                        # Verificar cancelación después de generar
                        if progress.fue_cancelado():
                            logger.info("Generación cancelada después de generar carnet PDF HTML")
                            break
                        
                        # Rastrear estado de OCR
                        if self.usar_ocr:
                            if "verificado" in mensaje_ocr.lower() or "verificación" in mensaje_ocr.lower():
                                if "incompleta" not in mensaje_ocr.lower() and "error" not in mensaje_ocr.lower():
                                    ocr_usado_exitosamente = True
                                else:
                                    errores_ocr += 1
                            elif "error" in mensaje_ocr.lower() or "no disponible" in mensaje_ocr.lower():
                                errores_ocr += 1
                        
                        if not exito or not ruta_png_final:
                            errores += 1
                            continue
                        
                        # Convertir PNG verificado a PDF
                        try:
                            imagen = Image.open(ruta_png_final)
                            if imagen.mode != 'RGB':
                                imagen = imagen.convert('RGB')
                            imagen.save(
                                ruta_pdf,
                                "PDF",
                                resolution=1200.0,
                                quality=100
                            )
                            archivos_generados.append(ruta_pdf)
                            exitosos += 1
                            
                            # Eliminar PNG temporal
                            try:
                                ruta_png_temp.unlink()
                            except:
                                pass
                        except Exception as e_pdf:
                            import logging
                            logging.getLogger(__name__).error(f"Error al convertir PNG a PDF: {e_pdf}")
                            errores += 1
                    else:
                        # Función para generar carnet con sistema PIL
                        def generar_carnet_pil():
                            img = self.designer.renderizar_carnet(
                                template=template,
                                nombre_empleado=emp['nombre_empleado'] or "SIN NOMBRE",
                                codigo_barras_path=str(codigo_path),
                                empresa=template.empresa_texto if template.mostrar_empresa else None,
                                web=template.web_texto if template.mostrar_web else None
                            )
                            # Escalar para alta calidad
                            if img:
                                factor_calidad = 1200 / 300.0
                                nuevo_ancho = int(img.size[0] * factor_calidad)
                                nuevo_alto = int(img.size[1] * factor_calidad)
                                img = img.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
                            return img
                    
                        # Verificar cancelación antes de generar
                        if progress.fue_cancelado():
                            logger.info("Generación cancelada antes de generar carnet PDF PIL")
                            break
                        
                        # Generar PNG temporal para verificación OCR
                        ruta_png_temp = ruta_pdf.with_suffix('.png')
                        exito, mensaje_ocr, ruta_png_final = self._generar_carnet_con_verificacion_ocr(
                            generar_carnet_pil,
                            emp,
                            ruta_png_temp,
                            verificar_ocr=self.usar_ocr,
                            max_reintentos=2,
                            progress_dialog=progress  # Pasar el diálogo para verificar cancelación
                        )
                        
                        # Verificar cancelación después de generar
                        if progress.fue_cancelado():
                            logger.info("Generación cancelada después de generar carnet PDF PIL")
                            break
                        
                        # Rastrear estado de OCR
                        if self.usar_ocr:
                            if "verificado" in mensaje_ocr.lower() or "verificación" in mensaje_ocr.lower():
                                if "incompleta" not in mensaje_ocr.lower() and "error" not in mensaje_ocr.lower():
                                    ocr_usado_exitosamente = True
                                else:
                                    errores_ocr += 1
                            elif "error" in mensaje_ocr.lower() or "no disponible" in mensaje_ocr.lower():
                                errores_ocr += 1
                        
                        if not exito or not ruta_png_final:
                            errores += 1
                            continue
                    
                        # Convertir PNG verificado a PDF
                        try:
                            imagen = Image.open(ruta_png_final)
                            if imagen.mode != 'RGB':
                                imagen = imagen.convert('RGB')
                            imagen.save(
                                ruta_pdf,
                                "PDF",
                                resolution=1200.0,
                                quality=100
                            )
                            archivos_generados.append(ruta_pdf)
                            exitosos += 1
                            
                            # Eliminar PNG temporal
                            try:
                                ruta_png_temp.unlink()
                            except:
                                pass
                        except Exception as e_pdf:
                            import logging
                            logging.getLogger(__name__).error(f"Error al convertir PNG a PDF: {e_pdf}")
                            errores += 1
                except Exception as e:
                    errores += 1
                    import logging
                    logger = logging.getLogger(__name__)
                    # Intentar obtener nombre del empleado para el log
                    try:
                        emp_error = self._desempaquetar_empleado(empleado)
                        nombre_error = emp_error['nombre_empleado'] if emp_error else "desconocido"
                    except:
                        nombre_error = "desconocido"
                    logger.error(f"Error al generar PDF para {nombre_error}: {e}")
            
            # Verificar si se canceló antes de comprimir
            if progress.fue_cancelado():
                logger.info("Generación masiva PDF cancelada antes de comprimir ZIP")
                if directorio_temp and directorio_temp.exists():
                    import shutil
                    try:
                        shutil.rmtree(directorio_temp)
                    except:
                        pass
                progress.close()
                QMessageBox.information(
                    self.employees_panel,
                    "Generación Cancelada",
                    f"Generación cancelada por el usuario.\n\n"
                    f"PDFs generados hasta el momento: {exitosos}\n"
                    f"Errores: {errores}"
                )
                return
            
            # Crear archivo ZIP con todos los PDFs generados
            if archivos_generados:
                progress.actualizar_progreso(total, total + 1, "Comprimiendo PDFs en ZIP...")
                QApplication.processEvents()
                
                # Verificar cancelación antes de comprimir
                if progress.fue_cancelado():
                    logger.info("Generación masiva PDF cancelada antes de comprimir ZIP")
                    if directorio_temp and directorio_temp.exists():
                        import shutil
                        try:
                            shutil.rmtree(directorio_temp)
                        except:
                            pass
                    progress.close()
                    QMessageBox.information(
                        self.employees_panel,
                        "Generación Cancelada",
                        f"Generación cancelada por el usuario.\n\n"
                        f"PDFs generados hasta el momento: {exitosos}\n"
                        f"Errores: {errores}"
                    )
                    return
                
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
        progress.marcar_completado()  # Marcar como completado antes de cerrar
        progress.close()
        
        mensaje = f"Generación completada:\n{exitosos} PDF(s) generado(s) y guardado(s) en:\n{ruta_zip_path}"
        
        # Mensaje de OCR basado en el estado real
        if self.usar_ocr:
            if ocr_usado_exitosamente and errores_ocr == 0:
                mensaje += f"\n\n✓ Verificación OCR: Habilitada (todos los PDFs fueron verificados)"
            elif ocr_usado_exitosamente and errores_ocr > 0:
                mensaje += f"\n\n⚠ Verificación OCR: Parcial (algunos PDFs no pudieron ser verificados: {errores_ocr} error(es))"
            else:
                mensaje += f"\n\n⚠ Verificación OCR: No disponible (Tesseract no está instalado o no está en PATH)"
        else:
            mensaje += f"\n\n⚠ Verificación OCR: No disponible (Tesseract no está instalado)"
        
        if errores > 0:
            mensaje += f"\n\n{errores} error(es) durante la generación"
        
        QMessageBox.information(self.employees_panel, "Resultado", mensaje)

