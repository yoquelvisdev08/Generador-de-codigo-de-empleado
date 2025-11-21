"""
Panel de gestión de usuarios integrado en la ventana principal
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QTableWidget,
                             QTableWidgetItem, QHeaderView,
                             QComboBox, QGroupBox, QSplitter)
from PyQt6.QtCore import Qt
import re

from src.models.database import DatabaseManager
from src.utils.password_utils import hash_contraseña, formatear_contraseña_hash
from src.utils.user_logger import user_logger
from src.utils.auth_utils import solicitar_autenticacion_admin


class UserManagementPanel(QWidget):
    """Panel de gestión de usuarios para administradores"""
    
    def __init__(self, usuario_actual: str, rol_actual: str = "admin", parent=None):
        """
        Inicializa el panel de gestión de usuarios
        
        Args:
            usuario_actual: Usuario actual autenticado
            rol_actual: Rol del usuario actual ('admin' o 'user')
            parent: Widget padre
        """
        super().__init__(parent)
        self.usuario_actual = usuario_actual
        self.rol_actual = rol_actual
        self.db_manager = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(5)
        layout_principal.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout_principal)
        
        # Splitter para paneles lado a lado
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # Panel izquierdo: Formulario
        self.crear_panel_formulario(splitter)
        
        # Panel derecho: Lista de usuarios
        self.crear_panel_usuarios(splitter)
        
        # Configurar tamaños proporcionales
        splitter.setSizes([400, 600])
        
        layout_principal.addWidget(splitter)
    
    def crear_panel_formulario(self, splitter):
        """Crea el panel de formulario para crear/editar usuarios"""
        panel_formulario = QGroupBox("Gestión de Usuario")
        
        layout_formulario = QVBoxLayout()
        layout_formulario.setSpacing(10)
        layout_formulario.setContentsMargins(15, 20, 15, 15)
        panel_formulario.setLayout(layout_formulario)
        
        # Selector de acción
        label_accion = QLabel("Acción:")
        layout_formulario.addWidget(label_accion)
        
        self.combo_accion = QComboBox()
        self.combo_accion.addItems(["Crear Nuevo Usuario", "Cambiar Contraseña"])
        self.combo_accion.currentIndexChanged.connect(self.cambiar_modo)
        layout_formulario.addWidget(self.combo_accion)
        
        layout_formulario.addSpacing(8)
        
        # Campos de formulario
        self.campo_nombre = self._crear_campo_con_label("Nombre completo:", layout_formulario)
        self.campo_email = self._crear_campo_con_label("Email:", layout_formulario)
        self.campo_usuario = self._crear_campo_con_label("Usuario:", layout_formulario)
        
        # Label y combo para seleccionar usuario (modo cambiar contraseña)
        self.label_seleccionar_usuario = QLabel("Seleccionar usuario:")
        self.label_seleccionar_usuario.setVisible(False)
        layout_formulario.addWidget(self.label_seleccionar_usuario)
        
        self.combo_usuario = QComboBox()
        self.combo_usuario.setVisible(False)
        layout_formulario.addWidget(self.combo_usuario)
        
        # Campos de contraseña
        self.campo_password = self._crear_campo_con_label("Contraseña:", layout_formulario, password=True)
        self.campo_confirmar_password = self._crear_campo_con_label("Confirmar contraseña:", layout_formulario, password=True)
        
        # Rol (solo para crear usuario)
        self.label_rol = QLabel("Rol:")
        layout_formulario.addWidget(self.label_rol)
        
        self.combo_rol = QComboBox()
        self.combo_rol.addItems(["admin", "user"])
        layout_formulario.addWidget(self.combo_rol)
        
        # Spacer flexible
        layout_formulario.addStretch()
        
        # Botones de acción
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(10)
        
        self.boton_limpiar = QPushButton("Limpiar")
        self.boton_limpiar.setMinimumHeight(35)
        self.boton_limpiar.clicked.connect(self.limpiar_formulario)
        layout_botones.addWidget(self.boton_limpiar)
        
        self.boton_guardar = QPushButton("Crear Usuario")
        self.boton_guardar.setMinimumHeight(35)
        self.boton_guardar.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; padding: 8px;")
        self.boton_guardar.clicked.connect(self.guardar_usuario)
        layout_botones.addWidget(self.boton_guardar)
        
        layout_formulario.addLayout(layout_botones)
        
        panel_formulario.setMaximumWidth(380)
        splitter.addWidget(panel_formulario)
    
    def crear_panel_usuarios(self, splitter):
        """Crea el panel de lista de usuarios"""
        panel_usuarios = QGroupBox("Usuarios Registrados")
        
        layout_usuarios = QVBoxLayout()
        layout_usuarios.setSpacing(10)
        layout_usuarios.setContentsMargins(15, 20, 15, 15)
        panel_usuarios.setLayout(layout_usuarios)
        
        # Tabla de usuarios
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(5)
        self.tabla_usuarios.setHorizontalHeaderLabels(["Usuario", "Nombre", "Email", "Rol", "Fecha Creación"])
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_usuarios.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_usuarios.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla_usuarios.setAlternatingRowColors(True)
        self.tabla_usuarios.setStyleSheet("""
            QTableWidget {
                border: 1px solid #444;
                background-color: #1e1e1e;
                gridline-color: #444;
                color: #ffffff;
            }
            QTableWidget::item {
                padding: 5px;
                color: #ffffff;
                background-color: #1e1e1e;
            }
            QTableWidget::item:alternate {
                background-color: #2d2d2d;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #444;
                font-weight: bold;
            }
        """)
        layout_usuarios.addWidget(self.tabla_usuarios)
        
        # Botones de acción
        layout_botones_tabla = QHBoxLayout()
        layout_botones_tabla.setSpacing(10)
        
        boton_refrescar = QPushButton("Refrescar")
        boton_refrescar.setMinimumHeight(35)
        boton_refrescar.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px;")
        boton_refrescar.clicked.connect(self.cargar_usuarios)
        layout_botones_tabla.addWidget(boton_refrescar)
        
        layout_botones_tabla.addStretch()
        
        self.boton_eliminar = QPushButton("Eliminar Usuario")
        self.boton_eliminar.setMinimumHeight(35)
        self.boton_eliminar.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold; padding: 8px;")
        self.boton_eliminar.clicked.connect(self.eliminar_usuario)
        layout_botones_tabla.addWidget(self.boton_eliminar)
        
        layout_usuarios.addLayout(layout_botones_tabla)
        
        splitter.addWidget(panel_usuarios)
    
    def _crear_campo_con_label(self, texto_label: str, layout_padre, password: bool = False):
        """Crea un campo de entrada con su label"""
        label = QLabel(texto_label)
        layout_padre.addWidget(label)
        
        campo = QLineEdit()
        if password:
            campo.setEchoMode(QLineEdit.EchoMode.Password)
        layout_padre.addWidget(campo)
        
        return campo
    
    
    def cambiar_modo(self):
        """Cambia entre modo crear usuario y cambiar contraseña"""
        es_modo_crear = self.combo_accion.currentIndex() == 0
        
        # Mostrar/ocultar campos según el modo
        self.campo_nombre.parent().layout().itemAt(
            self.campo_nombre.parent().layout().indexOf(self.campo_nombre) - 1
        ).widget().setVisible(es_modo_crear)
        self.campo_nombre.setVisible(es_modo_crear)
        
        self.campo_email.parent().layout().itemAt(
            self.campo_email.parent().layout().indexOf(self.campo_email) - 1
        ).widget().setVisible(es_modo_crear)
        self.campo_email.setVisible(es_modo_crear)
        
        self.campo_usuario.parent().layout().itemAt(
            self.campo_usuario.parent().layout().indexOf(self.campo_usuario) - 1
        ).widget().setVisible(es_modo_crear)
        self.campo_usuario.setVisible(es_modo_crear)
        
        self.label_rol.setVisible(es_modo_crear)
        self.combo_rol.setVisible(es_modo_crear)
        
        # Mostrar selector de usuario en modo cambiar contraseña
        self.label_seleccionar_usuario.setVisible(not es_modo_crear)
        self.combo_usuario.setVisible(not es_modo_crear)
        
        if not es_modo_crear:
            # Cargar usuarios en el combo
            self.cargar_usuarios_combo()
        
        # Actualizar texto del botón
        self.boton_guardar.setText("Crear Usuario" if es_modo_crear else "Cambiar Contraseña")
        
        self.limpiar_formulario()
    
    def cargar_usuarios_combo(self):
        """Carga los usuarios en el combo de selección"""
        self.combo_usuario.clear()
        usuarios = self.db_manager.obtener_todos_usuarios()
        for usuario in usuarios:
            self.combo_usuario.addItem(usuario['usuario'])
    
    def cargar_usuarios(self):
        """Carga los usuarios en la tabla"""
        usuarios = self.db_manager.obtener_todos_usuarios()
        
        self.tabla_usuarios.setRowCount(0)
        
        for usuario in usuarios:
            fila = self.tabla_usuarios.rowCount()
            self.tabla_usuarios.insertRow(fila)
            
            self.tabla_usuarios.setItem(fila, 0, QTableWidgetItem(usuario['usuario']))
            self.tabla_usuarios.setItem(fila, 1, QTableWidgetItem(usuario['nombre']))
            self.tabla_usuarios.setItem(fila, 2, QTableWidgetItem(usuario['email']))
            self.tabla_usuarios.setItem(fila, 3, QTableWidgetItem(usuario['rol']))
            
            fecha_str = str(usuario['fecha_creacion']).split('.')[0] if usuario['fecha_creacion'] else ""
            self.tabla_usuarios.setItem(fila, 4, QTableWidgetItem(fecha_str))
    
    def validar_email(self, email: str) -> bool:
        """Valida el formato de un email"""
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        self.campo_nombre.clear()
        self.campo_email.clear()
        self.campo_usuario.clear()
        self.campo_password.clear()
        self.campo_confirmar_password.clear()
    
    def guardar_usuario(self):
        """Guarda el usuario (crear nuevo o cambiar contraseña)"""
        es_modo_crear = self.combo_accion.currentIndex() == 0
        
        if es_modo_crear:
            self.crear_usuario()
        else:
            self.cambiar_contraseña()
    
    def crear_usuario(self):
        """Crea un nuevo usuario"""
        nombre = self.campo_nombre.text().strip()
        email = self.campo_email.text().strip()
        usuario = self.campo_usuario.text().strip()
        password = self.campo_password.text()
        confirmar_password = self.campo_confirmar_password.text()
        rol = self.combo_rol.currentText()
        
        # Validaciones
        if not nombre:
            QMessageBox.warning(self, "Advertencia", "Por favor ingrese el nombre completo")
            self.campo_nombre.setFocus()
            return
        
        if not email:
            QMessageBox.warning(self, "Advertencia", "Por favor ingrese el email")
            self.campo_email.setFocus()
            return
        
        if not self.validar_email(email):
            QMessageBox.warning(self, "Advertencia", "Por favor ingrese un email válido")
            self.campo_email.setFocus()
            return
        
        if not usuario:
            QMessageBox.warning(self, "Advertencia", "Por favor ingrese el nombre de usuario")
            self.campo_usuario.setFocus()
            return
        
        if len(usuario) < 3:
            QMessageBox.warning(self, "Advertencia", "El nombre de usuario debe tener al menos 3 caracteres")
            self.campo_usuario.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "Advertencia", "Por favor ingrese la contraseña")
            self.campo_password.setFocus()
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Advertencia", "La contraseña debe tener al menos 6 caracteres")
            self.campo_password.setFocus()
            return
        
        if password != confirmar_password:
            QMessageBox.warning(self, "Advertencia", "Las contraseñas no coinciden")
            self.campo_confirmar_password.clear()
            self.campo_confirmar_password.setFocus()
            return
        
        # Verificar si el usuario ya existe
        if self.db_manager.existe_usuario(usuario):
            QMessageBox.warning(self, "Error", "El nombre de usuario ya está en uso. Por favor elija otro.")
            self.campo_usuario.clear()
            self.campo_usuario.setFocus()
            return
        
        # Verificar si el email ya existe
        if self.db_manager.existe_email(email):
            QMessageBox.warning(self, "Error", "El email ya está registrado. Por favor use otro email.")
            self.campo_email.clear()
            self.campo_email.setFocus()
            return
        
        # Generar hash de la contraseña
        hash_hex, salt = hash_contraseña(password)
        contraseña_hash = formatear_contraseña_hash(hash_hex, salt)
        
        # Crear usuario
        exito = self.db_manager.crear_usuario(
            nombre=nombre,
            email=email,
            usuario=usuario,
            contraseña_hash=contraseña_hash,
            rol=rol
        )
        
        if exito:
            # Registrar acción
            user_logger.log_action(
                self.usuario_actual, 
                "crear_usuario", 
                f"Creado usuario: {usuario} con rol {rol}"
            )
            
            QMessageBox.information(
                self, 
                "Éxito",
                f"Usuario '{usuario}' creado correctamente con rol '{rol}'."
            )
            self.limpiar_formulario()
            self.cargar_usuarios()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "No se pudo crear el usuario. Por favor intente nuevamente."
            )
    
    def cambiar_contraseña(self):
        """Cambia la contraseña de un usuario existente"""
        usuario_seleccionado = self.combo_usuario.currentText()
        password = self.campo_password.text()
        confirmar_password = self.campo_confirmar_password.text()
        
        if not usuario_seleccionado:
            QMessageBox.warning(self, "Advertencia", "Por favor seleccione un usuario")
            return
        
        if not password:
            QMessageBox.warning(self, "Advertencia", "Por favor ingrese la nueva contraseña")
            self.campo_password.setFocus()
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Advertencia", "La contraseña debe tener al menos 6 caracteres")
            self.campo_password.setFocus()
            return
        
        if password != confirmar_password:
            QMessageBox.warning(self, "Advertencia", "Las contraseñas no coinciden")
            self.campo_confirmar_password.clear()
            self.campo_confirmar_password.setFocus()
            return
        
        # Confirmar cambio de contraseña
        respuesta = QMessageBox.question(
            self,
            "Confirmar Cambio de Contraseña",
            f"¿Está seguro de que desea cambiar la contraseña del usuario '{usuario_seleccionado}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        
        # Generar hash de la nueva contraseña
        hash_hex, salt = hash_contraseña(password)
        contraseña_hash = formatear_contraseña_hash(hash_hex, salt)
        
        # Actualizar contraseña
        exito = self.db_manager.actualizar_contraseña_usuario(usuario_seleccionado, contraseña_hash)
        
        if exito:
            # Registrar acción
            user_logger.log_action(
                self.usuario_actual,
                "cambiar_contraseña",
                f"Contraseña cambiada para usuario: {usuario_seleccionado}"
            )
            
            QMessageBox.information(
                self,
                "Éxito",
                f"Contraseña actualizada correctamente para el usuario '{usuario_seleccionado}'."
            )
            self.limpiar_formulario()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "No se pudo actualizar la contraseña. Por favor intente nuevamente."
            )
    
    def eliminar_usuario(self):
        """Elimina el usuario seleccionado"""
        fila_seleccionada = self.tabla_usuarios.currentRow()
        
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Advertencia", "Por favor seleccione un usuario de la tabla")
            return
        
        usuario_seleccionado = self.tabla_usuarios.item(fila_seleccionada, 0).text()
        
        # No permitir eliminar el usuario actual
        if usuario_seleccionado == self.usuario_actual:
            QMessageBox.warning(
                self,
                "Advertencia",
                "No puede eliminar su propio usuario. Por favor seleccione otro usuario."
            )
            return
        
        # Verificar autenticación de administrador antes de eliminar
        if not solicitar_autenticacion_admin(
            self,
            f"eliminar el usuario '{usuario_seleccionado}'",
            self.usuario_actual,
            self.rol_actual
        ):
            return
        
        # Confirmar eliminación
        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar el usuario '{usuario_seleccionado}'?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        
        # Eliminar usuario
        exito = self.db_manager.eliminar_usuario(usuario_seleccionado)
        
        if exito:
            # Registrar acción
            user_logger.log_action(
                self.usuario_actual,
                "eliminar_usuario",
                f"Eliminado usuario: {usuario_seleccionado}"
            )
            
            QMessageBox.information(
                self,
                "Éxito",
                f"Usuario '{usuario_seleccionado}' eliminado correctamente."
            )
            self.cargar_usuarios()
            self.cargar_usuarios_combo()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "No se pudo eliminar el usuario. Por favor intente nuevamente."
            )

