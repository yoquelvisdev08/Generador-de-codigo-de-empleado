"""
Panel de controles de diseño del carnet
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QPushButton, 
                             QLabel, QLineEdit, QSpinBox, QColorDialog, QFileDialog,
                             QCheckBox, QComboBox, QHBoxLayout, QDoubleSpinBox, QScrollArea,
                             QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from pathlib import Path
from typing import Optional

from src.models.carnet_template import CarnetTemplate
from src.models.html_template import HTMLTemplate
from src.utils.template_generator import generar_html_ejemplo
from config.settings import TEMPLATES_DIR


class CarnetControlsPanel(QWidget):
    """Panel con controles para diseñar el carnet"""
    
    def __init__(self, parent=None):
        """
        Inicializa el panel de controles
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.template = CarnetTemplate()
        self.html_template = HTMLTemplate()
        self.usar_html = False  # Flag para saber si usar HTML o template Python
        self.callback_actualizacion = None  # Callback para actualizar vista previa
        self.init_ui()
        self._cargar_template_default()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Scroll area para los controles
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_widget.setLayout(scroll_layout)
        
        # Grupo único: Template HTML y Variables
        grupo_template = QGroupBox("Template HTML y Variables")
        layout_template = QVBoxLayout()
        grupo_template.setLayout(layout_template)
        
        # Sección: Template HTML
        self.boton_cargar_html = QPushButton("Cargar Template HTML")
        self.boton_cargar_html.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; padding: 8px;")
        self.boton_cargar_html.clicked.connect(self.cargar_template_html)
        layout_template.addWidget(self.boton_cargar_html)
        
        self.boton_exportar_ejemplo = QPushButton("Exportar HTML de Ejemplo")
        self.boton_exportar_ejemplo.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px;")
        self.boton_exportar_ejemplo.clicked.connect(self.exportar_html_ejemplo)
        layout_template.addWidget(self.boton_exportar_ejemplo)
        
        self.label_template_cargado = QLabel("Ningún template HTML cargado")
        self.label_template_cargado.setWordWrap(True)
        self.label_template_cargado.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        layout_template.addWidget(self.label_template_cargado)
        
        # Separador visual
        separador = QLabel("─────────────────────────────────────")
        separador.setStyleSheet("color: #ddd; padding: 10px 0px;")
        layout_template.addWidget(separador)
        
        # Sección: Variables del Template
        info_variables = QLabel(
            "Las variables se detectan automáticamente del template HTML.\n"
            "El estilo se modifica editando el archivo HTML directamente."
        )
        info_variables.setWordWrap(True)
        info_variables.setStyleSheet("color: #666; font-size: 10pt; padding: 5px;")
        layout_template.addWidget(info_variables)
        
        # Contenedor para campos de variables dinámicos
        self.variables_widget = QWidget()
        self.variables_layout = QVBoxLayout()
        self.variables_layout.setSpacing(6)
        self.variables_layout.setContentsMargins(10, 10, 10, 10)
        self.variables_widget.setLayout(self.variables_layout)
        layout_template.addWidget(self.variables_widget)
        
        # Diccionario para almacenar los campos de variables dinámicos
        self.campos_variables = {}
        
        # Guardar referencia al layout de variables para uso en otros métodos
        self.layout_variables = layout_template
        
        scroll_layout.addWidget(grupo_template)
        
        # Grupo: Logo (solo para template PIL, oculto cuando se usa HTML)
        grupo_logo = QGroupBox("Logo")
        layout_logo = QVBoxLayout()
        grupo_logo.setLayout(layout_logo)
        
        self.boton_cargar_logo = QPushButton("Cargar Logo")
        self.boton_cargar_logo.clicked.connect(self.cargar_logo)
        layout_logo.addWidget(self.boton_cargar_logo)
        
        layout_logo_pos = QHBoxLayout()
        layout_logo_pos.addWidget(QLabel("X:"))
        self.spin_logo_x = QSpinBox()
        self.spin_logo_x.setRange(0, 2000)
        self.spin_logo_x.setValue(self.template.logo_x)
        layout_logo_pos.addWidget(self.spin_logo_x)
        
        layout_logo_pos.addWidget(QLabel("Y:"))
        self.spin_logo_y = QSpinBox()
        self.spin_logo_y.setRange(0, 2000)
        self.spin_logo_y.setValue(self.template.logo_y)
        layout_logo_pos.addWidget(self.spin_logo_y)
        layout_logo.addLayout(layout_logo_pos)
        
        layout_logo_tam = QHBoxLayout()
        layout_logo_tam.addWidget(QLabel("Ancho:"))
        self.spin_logo_ancho = QSpinBox()
        self.spin_logo_ancho.setRange(10, 500)
        self.spin_logo_ancho.setValue(self.template.logo_ancho)
        layout_logo_tam.addWidget(self.spin_logo_ancho)
        
        layout_logo_tam.addWidget(QLabel("Alto:"))
        self.spin_logo_alto = QSpinBox()
        self.spin_logo_alto.setRange(10, 500)
        self.spin_logo_alto.setValue(self.template.logo_alto)
        layout_logo_tam.addWidget(self.spin_logo_alto)
        layout_logo.addLayout(layout_logo_tam)
        
        scroll_layout.addWidget(grupo_logo)
        
        # Grupo: Fondo
        grupo_fondo = QGroupBox("Fondo")
        layout_fondo = QVBoxLayout()
        grupo_fondo.setLayout(layout_fondo)
        
        self.boton_color_fondo = QPushButton("Color de Fondo")
        self.boton_color_fondo.clicked.connect(self.seleccionar_color_fondo)
        layout_fondo.addWidget(self.boton_color_fondo)
        
        self.boton_imagen_fondo = QPushButton("Imagen de Fondo")
        self.boton_imagen_fondo.clicked.connect(self.cargar_imagen_fondo)
        layout_fondo.addWidget(self.boton_imagen_fondo)
        
        layout_opacidad = QHBoxLayout()
        layout_opacidad.addWidget(QLabel("Opacidad:"))
        self.spin_opacidad = QDoubleSpinBox()
        self.spin_opacidad.setRange(0.0, 1.0)
        self.spin_opacidad.setSingleStep(0.1)
        self.spin_opacidad.setValue(self.template.fondo_opacidad)
        layout_opacidad.addWidget(self.spin_opacidad)
        layout_fondo.addLayout(layout_opacidad)
        
        scroll_layout.addWidget(grupo_fondo)
        
        # Grupo: Nombre
        grupo_nombre = QGroupBox("Nombre del Empleado")
        layout_nombre = QVBoxLayout()
        grupo_nombre.setLayout(layout_nombre)
        
        self.check_mostrar_nombre = QCheckBox("Mostrar Nombre")
        self.check_mostrar_nombre.setChecked(self.template.mostrar_nombre)
        layout_nombre.addWidget(self.check_mostrar_nombre)
        
        layout_nombre_pos = QHBoxLayout()
        layout_nombre_pos.addWidget(QLabel("X:"))
        self.spin_nombre_x = QSpinBox()
        self.spin_nombre_x.setRange(0, 2000)
        self.spin_nombre_x.setValue(self.template.nombre_x)
        layout_nombre_pos.addWidget(self.spin_nombre_x)
        
        layout_nombre_pos.addWidget(QLabel("Y:"))
        self.spin_nombre_y = QSpinBox()
        self.spin_nombre_y.setRange(0, 2000)
        self.spin_nombre_y.setValue(self.template.nombre_y)
        layout_nombre_pos.addWidget(self.spin_nombre_y)
        layout_nombre.addLayout(layout_nombre_pos)
        
        layout_nombre_fuente = QHBoxLayout()
        layout_nombre_fuente.addWidget(QLabel("Tamaño:"))
        self.spin_nombre_tamaño = QSpinBox()
        self.spin_nombre_tamaño.setRange(8, 72)
        self.spin_nombre_tamaño.setValue(self.template.nombre_tamaño)
        layout_nombre_fuente.addWidget(self.spin_nombre_tamaño)
        
        self.boton_color_nombre = QPushButton("Color")
        self.boton_color_nombre.clicked.connect(self.seleccionar_color_nombre)
        layout_nombre_fuente.addWidget(self.boton_color_nombre)
        layout_nombre.addLayout(layout_nombre_fuente)
        
        scroll_layout.addWidget(grupo_nombre)
        
        # Grupo: Código de Barras
        grupo_codigo = QGroupBox("Código de Barras")
        layout_codigo = QVBoxLayout()
        grupo_codigo.setLayout(layout_codigo)
        
        layout_codigo_pos = QHBoxLayout()
        layout_codigo_pos.addWidget(QLabel("X:"))
        self.spin_codigo_x = QSpinBox()
        self.spin_codigo_x.setRange(0, 2000)
        self.spin_codigo_x.setValue(self.template.codigo_barras_x)
        layout_codigo_pos.addWidget(self.spin_codigo_x)
        
        layout_codigo_pos.addWidget(QLabel("Y:"))
        self.spin_codigo_y = QSpinBox()
        self.spin_codigo_y.setRange(0, 2000)
        self.spin_codigo_y.setValue(self.template.codigo_barras_y)
        layout_codigo_pos.addWidget(self.spin_codigo_y)
        layout_codigo.addLayout(layout_codigo_pos)
        
        layout_codigo_tam = QHBoxLayout()
        layout_codigo_tam.addWidget(QLabel("Ancho:"))
        self.spin_codigo_ancho = QSpinBox()
        self.spin_codigo_ancho.setRange(50, 800)
        self.spin_codigo_ancho.setValue(self.template.codigo_barras_ancho)
        layout_codigo_tam.addWidget(self.spin_codigo_ancho)
        
        layout_codigo_tam.addWidget(QLabel("Alto:"))
        self.spin_codigo_alto = QSpinBox()
        self.spin_codigo_alto.setRange(20, 300)
        self.spin_codigo_alto.setValue(self.template.codigo_barras_alto)
        layout_codigo_tam.addWidget(self.spin_codigo_alto)
        layout_codigo.addLayout(layout_codigo_tam)
        
        self.check_mostrar_numero = QCheckBox("Mostrar Número del Código")
        self.check_mostrar_numero.setChecked(self.template.mostrar_numero_codigo)
        layout_codigo.addWidget(self.check_mostrar_numero)
        
        scroll_layout.addWidget(grupo_codigo)
        
        # Grupo: Información Adicional
        grupo_info = QGroupBox("Información Adicional")
        layout_info = QVBoxLayout()
        grupo_info.setLayout(layout_info)
        
        self.check_mostrar_empresa = QCheckBox("Mostrar Empresa")
        self.check_mostrar_empresa.setChecked(self.template.mostrar_empresa)
        layout_info.addWidget(self.check_mostrar_empresa)
        
        self.campo_empresa = QLineEdit()
        self.campo_empresa.setPlaceholderText("Nombre de la empresa")
        self.campo_empresa.setText(self.template.empresa_texto)
        layout_info.addWidget(self.campo_empresa)
        
        self.check_mostrar_web = QCheckBox("Mostrar Sitio Web")
        self.check_mostrar_web.setChecked(self.template.mostrar_web)
        layout_info.addWidget(self.check_mostrar_web)
        
        self.campo_web = QLineEdit()
        self.campo_web.setPlaceholderText("www.ejemplo.com")
        self.campo_web.setText(self.template.web_texto)
        layout_info.addWidget(self.campo_web)
        
        scroll_layout.addWidget(grupo_info)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
    
    def cargar_logo(self):
        """Abre diálogo para cargar logo"""
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Logo", "", "Imágenes (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if archivo:
            self.template.logo_path = archivo
            self.boton_cargar_logo.setText(f"Logo: {Path(archivo).name}")
    
    def cargar_imagen_fondo(self):
        """Abre diálogo para cargar imagen de fondo"""
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen de Fondo", "", "Imágenes (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if archivo:
            self.template.fondo_imagen_path = archivo
            self.boton_imagen_fondo.setText(f"Fondo: {Path(archivo).name}")
    
    def seleccionar_color_fondo(self):
        """Abre diálogo para seleccionar color de fondo"""
        color = QColorDialog.getColor(QColor(self.template.fondo_color), self, "Seleccionar Color de Fondo")
        if color.isValid():
            self.template.fondo_color = color.name()
            self.boton_color_fondo.setStyleSheet(f"background-color: {color.name()}; color: white;")
    
    def seleccionar_color_nombre(self):
        """Abre diálogo para seleccionar color del nombre"""
        color = QColorDialog.getColor(QColor(self.template.nombre_color), self, "Seleccionar Color del Nombre")
        if color.isValid():
            self.template.nombre_color = color.name()
            self.boton_color_nombre.setStyleSheet(f"background-color: {color.name()}; color: white;")
    
    def obtener_template_actualizado(self) -> CarnetTemplate:
        """Obtiene el template con los valores actuales de los controles"""
        # Actualizar valores del template desde los controles
        self.template.logo_x = self.spin_logo_x.value()
        self.template.logo_y = self.spin_logo_y.value()
        self.template.logo_ancho = self.spin_logo_ancho.value()
        self.template.logo_alto = self.spin_logo_alto.value()
        
        self.template.fondo_opacidad = self.spin_opacidad.value()
        
        self.template.mostrar_nombre = self.check_mostrar_nombre.isChecked()
        self.template.nombre_x = self.spin_nombre_x.value()
        self.template.nombre_y = self.spin_nombre_y.value()
        self.template.nombre_tamaño = self.spin_nombre_tamaño.value()
        
        self.template.codigo_barras_x = self.spin_codigo_x.value()
        self.template.codigo_barras_y = self.spin_codigo_y.value()
        self.template.codigo_barras_ancho = self.spin_codigo_ancho.value()
        self.template.codigo_barras_alto = self.spin_codigo_alto.value()
        self.template.mostrar_numero_codigo = self.check_mostrar_numero.isChecked()
        
        self.template.mostrar_empresa = self.check_mostrar_empresa.isChecked()
        self.template.empresa_texto = self.campo_empresa.text()
        
        self.template.mostrar_web = self.check_mostrar_web.isChecked()
        self.template.web_texto = self.campo_web.text()
        
        return self.template
    
    def cargar_template_html(self):
        """Abre diálogo para cargar un template HTML"""
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Template HTML", str(TEMPLATES_DIR), "Archivos HTML (*.html *.htm)"
        )
        if archivo:
            ruta = Path(archivo)
            if self.html_template.cargar_desde_archivo(ruta):
                self.usar_html = True
                self.label_template_cargado.setText(f"Template cargado: {ruta.name}")
                self.label_template_cargado.setStyleSheet("color: #28a745; font-weight: bold; padding: 5px;")
                self._actualizar_visibilidad_controles()
                # Generar campos de variables dinámicamente
                self._generar_campos_variables()
                if self.callback_actualizacion:
                    self.callback_actualizacion()
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", "No se pudo cargar el template HTML")
    
    def exportar_html_ejemplo(self):
        """Exporta un HTML de ejemplo que el usuario puede modificar"""
        archivo, _ = QFileDialog.getSaveFileName(
            self, "Guardar HTML de Ejemplo", str(TEMPLATES_DIR / "carnet_ejemplo.html"), "Archivos HTML (*.html)"
        )
        if archivo:
            try:
                html_ejemplo = generar_html_ejemplo()
                Path(archivo).write_text(html_ejemplo, encoding='utf-8')
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"HTML de ejemplo exportado exitosamente:\n{archivo}\n\n"
                    "Puedes abrir este archivo en un editor de texto o navegador para modificarlo."
                )
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", f"No se pudo exportar el HTML: {str(e)}")
    
    def obtener_html_template(self) -> Optional[HTMLTemplate]:
        """Obtiene el template HTML si está cargado"""
        if self.usar_html and self.html_template.ruta_html:
            return self.html_template
        return None
    
    def usar_template_html(self) -> bool:
        """Indica si se debe usar template HTML"""
        return self.usar_html and self.html_template.ruta_html is not None
    
    def _cargar_template_default(self):
        """Carga el template HTML por defecto"""
        template_default = TEMPLATES_DIR / "carnet_default.html"
        if not template_default.exists():
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Template por defecto no encontrado: {template_default}")
            self.label_template_cargado.setText("Template por defecto no encontrado")
            self.label_template_cargado.setStyleSheet("color: #dc3545; font-weight: bold; padding: 5px;")
            return
        
        if self.html_template.cargar_desde_archivo(template_default):
            self.usar_html = True
            self.label_template_cargado.setText(f"Template cargado: {template_default.name}")
            self.label_template_cargado.setStyleSheet("color: #28a745; font-weight: bold; padding: 5px;")
            self._actualizar_visibilidad_controles()
            # Generar campos de variables dinámicamente
            self._generar_campos_variables()
            # Notificar que se cargó el template para actualizar vista previa
            if self.callback_actualizacion:
                # Usar QTimer para ejecutar después de que la UI esté lista
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(500, self.callback_actualizacion)  # Aumentado a 500ms
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"No se pudo cargar el template: {template_default}")
            self.label_template_cargado.setText("Error al cargar template")
            self.label_template_cargado.setStyleSheet("color: #dc3545; font-weight: bold; padding: 5px;")
    
    def _actualizar_visibilidad_controles(self):
        """Muestra/oculta controles según si se usa HTML o PIL"""
        # Ocultar todos los grupos de estilo cuando se usa HTML
        grupos_estilo = [
            self.findChild(QGroupBox, "Logo"),
            self.findChild(QGroupBox, "Fondo"),
            self.findChild(QGroupBox, "Nombre del Empleado"),
            self.findChild(QGroupBox, "Código de Barras"),
            self.findChild(QGroupBox, "Información Adicional")
        ]
        
        # Buscar grupos manualmente
        for widget in self.findChildren(QGroupBox):
            if widget.title() in ["Logo", "Fondo", "Nombre del Empleado", "Código de Barras", "Información Adicional"]:
                widget.setVisible(not self.usar_html)
        
        # Mostrar grupo de template cuando se usa HTML (ya está siempre visible, pero podemos ajustar si es necesario)
        # El grupo template siempre está visible, solo ocultamos los controles PIL
    
    def _on_variable_changed(self):
        """Se ejecuta cuando cambia una variable"""
        if self.callback_actualizacion:
            self.callback_actualizacion()
    
    def establecer_callback_actualizacion(self, callback):
        """Establece el callback para actualizar la vista previa"""
        self.callback_actualizacion = callback
    
    def _generar_campos_variables(self):
        """Genera campos de variables dinámicamente según el template HTML"""
        # Limpiar campos existentes de forma más agresiva
        for campo in self.campos_variables.values():
            if isinstance(campo, dict):
                # Si es un diccionario (variable de imagen), eliminar los widgets
                if "campo" in campo:
                    campo["campo"].setParent(None)
                    campo["campo"].deleteLater()
            else:
                campo.setParent(None)
                campo.deleteLater()
        self.campos_variables.clear()
        
        # Limpiar layout completamente - eliminar todos los items
        while self.variables_layout.count():
            item = self.variables_layout.takeAt(0)
            if item is None:
                continue
            if item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                layout = item.layout()
                if layout:
                    while layout.count():
                        sub_item = layout.takeAt(0)
                        if sub_item is None:
                            continue
                        widget = sub_item.widget()
                        if widget:
                            widget.setParent(None)
                            widget.deleteLater()
                    layout.setParent(None)
        
        # Forzar actualización
        QApplication.processEvents()
        
        # Si no hay template HTML cargado, no generar campos
        if not self.usar_html or not self.html_template.ruta_html:
            return
        
        # Detectar variables del template
        variables = self.html_template.detectar_variables()
        
        # Variables de tipo imagen (permiten subir archivos)
        variables_imagen = {"logo", "foto", "codigo_barras"}
        
        # Variables automáticas de solo lectura (vienen de la base de datos)
        variables_automaticas = {"id_unico", "codigo_barras"}
        
        # Ordenar variables para mostrar primero las más comunes
        orden_preferido = ["logo", "nombre", "cedula", "cargo", "empresa", "web", "id_unico", "codigo_barras", "foto", "descripcion"]
        variables_ordenadas = sorted(
            variables,
            key=lambda x: (orden_preferido.index(x) if x in orden_preferido else 999, x)
        )
        
        # Estilos modernos para campos
        estilo_campo_texto = """
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 11pt;
                color: #333333;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
                background-color: #f8f9fa;
            }
            QLineEdit:hover {
                border: 2px solid #c0c0c0;
            }
        """
        
        estilo_campo_readonly = """
            QLineEdit {
                background-color: #f5f5f5;
                border: 2px solid #d0d0d0;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 11pt;
                color: #6c757d;
                min-height: 20px;
            }
        """
        
        estilo_boton_primario = """
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 10pt;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """
        
        estilo_boton_secundario = """
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #484f54;
            }
        """
        
        estilo_boton_peligro = """
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """
        
        # Generar campos para cada variable
        for var in variables_ordenadas:
            # Contenedor vertical para cada variable
            layout_var = QVBoxLayout()
            layout_var.setSpacing(4)
            layout_var.setContentsMargins(0, 4, 0, 4)
            
            # Label con nombre de variable (arriba del campo)
            label = QLabel(f"{var.replace('_', ' ').title()}:")
            label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 11pt;
                    color: #ffffff;
                    margin-bottom: 2px;
                }
            """)
            layout_var.addWidget(label)
            
            # Si es una variable de imagen, mostrar botón para cargar imagen
            if var in variables_imagen:
                # Campo para mostrar la ruta
                campo_ruta = QLineEdit()
                campo_ruta.setMinimumHeight(40)
                if var == "codigo_barras":
                    campo_ruta.setPlaceholderText("Se genera automáticamente desde la base de datos")
                elif var == "foto":
                    campo_ruta.setPlaceholderText("Ninguna foto seleccionada (opcional)")
                else:
                    campo_ruta.setPlaceholderText("Ninguna imagen seleccionada")
                campo_ruta.setReadOnly(var in variables_automaticas)
                
                if var in variables_automaticas:
                    campo_ruta.setStyleSheet(estilo_campo_readonly)
                else:
                    campo_ruta.setStyleSheet(estilo_campo_texto)
                
                layout_var.addWidget(campo_ruta)
                
                # Botones debajo del campo (solo si no es automática)
                if var not in variables_automaticas:
                    layout_botones = QHBoxLayout()
                    layout_botones.setSpacing(10)
                    layout_botones.setContentsMargins(0, 0, 0, 0)
                    
                    boton_cargar = QPushButton("Cargar Imagen")
                    boton_cargar.setStyleSheet(estilo_boton_primario)
                    boton_cargar.clicked.connect(lambda checked, v=var, c=campo_ruta: self._cargar_imagen_variable(v, c))
                    
                    boton_limpiar = QPushButton("Limpiar")
                    boton_limpiar.setStyleSheet(estilo_boton_peligro)
                    boton_limpiar.setToolTip("Limpiar imagen")
                    boton_limpiar.clicked.connect(lambda checked, v=var, c=campo_ruta: self._limpiar_imagen_variable(v, c))
                    
                    layout_botones.addWidget(boton_cargar)
                    layout_botones.addWidget(boton_limpiar)
                    layout_botones.addStretch()
                    
                    layout_var.addLayout(layout_botones)
                else:
                    # Para variables automáticas, mostrar un label informativo
                    label_info = QLabel("(Se obtiene automáticamente de la base de datos)")
                    label_info.setStyleSheet("""
                        QLabel {
                            color: #6c757d;
                            font-style: italic;
                            font-size: 9pt;
                            padding: 4px 0px;
                        }
                    """)
                    layout_var.addWidget(label_info)
                
                # Guardar tanto el campo como el Path
                self.campos_variables[var] = {"campo": campo_ruta, "path": None}
            else:
                # Campo de texto normal
                campo = QLineEdit()
                campo.setMinimumHeight(40)
                
                if var in variables_automaticas:
                    # Variable automática: solo lectura
                    campo.setReadOnly(True)
                    campo.setPlaceholderText(f"{{{{{var}}}}} (se obtiene de la base de datos)")
                    campo.setStyleSheet(estilo_campo_readonly)
                    
                    # Agregar label informativo debajo
                    label_info = QLabel("(Se obtiene automáticamente de la base de datos)")
                    label_info.setStyleSheet("""
                        QLabel {
                            color: #6c757d;
                            font-style: italic;
                            font-size: 9pt;
                            padding: 4px 0px;
                        }
                    """)
                    layout_var.addWidget(campo)
                    layout_var.addWidget(label_info)
                else:
                    # Variable editable
                    campo.setPlaceholderText(f"Ingrese el valor para {var.replace('_', ' ')}")
                    campo.setStyleSheet(estilo_campo_texto)
                    campo.textChanged.connect(self._on_variable_changed)
                    layout_var.addWidget(campo)
                
                self.campos_variables[var] = campo
            
            self.variables_layout.addLayout(layout_var)
        
        # Si no hay variables, mostrar mensaje
        if not variables:
            label_vacio = QLabel("No se encontraron variables en el template")
            label_vacio.setStyleSheet("color: #999; font-style: italic; padding: 10px;")
            self.variables_layout.addWidget(label_vacio)
        
        # Forzar actualización del layout
        self.variables_widget.updateGeometry()
        QApplication.processEvents()
    
    def _cargar_imagen_variable(self, variable: str, campo_ruta: QLineEdit):
        """Abre diálogo para cargar una imagen para una variable"""
        archivo, _ = QFileDialog.getOpenFileName(
            self, 
            f"Seleccionar Imagen para {variable.capitalize()}", 
            "", 
            "Archivos de Imagen (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if archivo:
            ruta = Path(archivo)
            if ruta.exists():
                campo_ruta.setText(str(ruta))
                # Guardar el Path en el diccionario
                if isinstance(self.campos_variables[variable], dict):
                    self.campos_variables[variable]["path"] = ruta
                self._on_variable_changed()
    
    def _limpiar_imagen_variable(self, variable: str, campo_ruta: QLineEdit):
        """Limpia la imagen seleccionada para una variable"""
        campo_ruta.clear()
        if isinstance(self.campos_variables[variable], dict):
            self.campos_variables[variable]["path"] = None
        self._on_variable_changed()
    
    def obtener_variables_html(self) -> dict:
        """Obtiene las variables HTML editadas por el usuario"""
        resultado = {}
        for var, campo in self.campos_variables.items():
            if isinstance(campo, dict):
                # Es una variable de imagen, retornar el Path
                resultado[var] = campo.get("path", None)
            else:
                # Es un campo de texto normal
                resultado[var] = campo.text()
        return resultado

