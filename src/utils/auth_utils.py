"""
Utilidades de autenticación
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from config.settings import autenticar_usuario


class AdminAuthDialog(QDialog):
    """Diálogo para solicitar autenticación de administrador"""
    
    def __init__(self, parent=None, accion: str = "realizar esta acción"):
        """
        Inicializa el diálogo de autenticación
        
        Args:
            parent: Widget padre
            accion: Descripción de la acción que requiere autenticación
        """
        super().__init__(parent)
        self.accion = accion
        self.usuario_autenticado = None
        self.rol_autenticado = None
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Autenticación de Administrador Requerida")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        self.setLayout(layout)
        
        label_info = QLabel(
            f"Se requiere autenticación de administrador para {self.accion}.\n\n"
            "Por favor ingrese sus credenciales de administrador:"
        )
        label_info.setWordWrap(True)
        layout.addWidget(label_info)
        
        # Campo de usuario
        layout_usuario = QVBoxLayout()
        label_usuario = QLabel("Usuario:")
        layout_usuario.addWidget(label_usuario)
        
        self.campo_usuario = QLineEdit()
        self.campo_usuario.setPlaceholderText("Ingrese su usuario")
        self.campo_usuario.returnPressed.connect(lambda: self.campo_password.setFocus())
        layout_usuario.addWidget(self.campo_usuario)
        layout.addLayout(layout_usuario)
        
        # Campo de contraseña
        layout_password = QVBoxLayout()
        label_password = QLabel("Contraseña:")
        layout_password.addWidget(label_password)
        
        self.campo_password = QLineEdit()
        self.campo_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.campo_password.setPlaceholderText("Ingrese su contraseña")
        self.campo_password.returnPressed.connect(self.verificar_autenticacion)
        layout_password.addWidget(self.campo_password)
        layout.addLayout(layout_password)
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_aceptar = QPushButton("Aceptar")
        boton_aceptar.clicked.connect(self.verificar_autenticacion)
        boton_aceptar.setDefault(True)
        layout_botones.addWidget(boton_aceptar)
        
        boton_cancelar = QPushButton("Cancelar")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        layout.addLayout(layout_botones)
        
        # Enfocar el campo de usuario al abrir
        self.campo_usuario.setFocus()
    
    def verificar_autenticacion(self):
        """Verifica las credenciales ingresadas contra la base de datos"""
        usuario_ingresado = self.campo_usuario.text().strip()
        password_ingresada = self.campo_password.text()
        
        if not usuario_ingresado:
            QMessageBox.warning(
                self, "Campo Requerido",
                "Por favor ingrese su usuario."
            )
            self.campo_usuario.setFocus()
            return
        
        if not password_ingresada:
            QMessageBox.warning(
                self, "Campo Requerido",
                "Por favor ingrese su contraseña."
            )
            self.campo_password.setFocus()
            return
        
        # Autenticar contra la base de datos
        es_valido, rol = autenticar_usuario(usuario_ingresado, password_ingresada)
        
        if not es_valido:
            QMessageBox.warning(
                self, "Credenciales Incorrectas",
                "El usuario o la contraseña son incorrectos.\n"
                "Por favor intente nuevamente."
            )
            self.campo_password.clear()
            self.campo_password.setFocus()
            return
        
        # Verificar que el usuario sea administrador
        if rol != "admin":
            QMessageBox.warning(
                self, "Permisos Insuficientes",
                f"El usuario '{usuario_ingresado}' no tiene permisos de administrador.\n\n"
                "Solo los administradores pueden realizar esta acción."
            )
            self.campo_password.clear()
            self.campo_password.setFocus()
            return
        
        # Autenticación exitosa
        self.usuario_autenticado = usuario_ingresado
        self.rol_autenticado = rol
        self.accept()
    
    def get_usuario_autenticado(self) -> str:
        """Retorna el usuario autenticado"""
        return self.usuario_autenticado
    
    def get_rol_autenticado(self) -> str:
        """Retorna el rol del usuario autenticado"""
        return self.rol_autenticado


def solicitar_autenticacion_admin(parent=None, accion: str = "realizar esta acción", 
                                   usuario_actual: str = None, rol_actual: str = None) -> bool:
    """
    Solicita autenticación de administrador para realizar una acción
    
    Primero verifica si el usuario actual es admin. Si no lo es, muestra un mensaje
    y retorna False. Si lo es, pide autenticación (usuario y contraseña) y verifica
    que el usuario autenticado sea admin.
    
    Args:
        parent: Widget padre para el diálogo
        accion: Descripción de la acción que requiere autenticación
        usuario_actual: Usuario actualmente autenticado en la aplicación
        rol_actual: Rol del usuario actualmente autenticado
        
    Returns:
        True si la autenticación es exitosa y el usuario es admin, False en caso contrario
    """
    # Si se proporciona usuario y rol actual, verificar primero que sea admin
    if usuario_actual is not None and rol_actual is not None:
        if rol_actual != "admin":
            QMessageBox.warning(
                parent, "Permisos Insuficientes",
                f"El usuario '{usuario_actual}' no tiene permisos de administrador.\n\n"
                f"Solo los administradores pueden {accion}.\n\n"
                "Si necesita realizar esta acción, contacte a un administrador."
            )
            return False
    
    # Pedir autenticación
    dialog = AdminAuthDialog(parent, accion)
    resultado = dialog.exec()
    
    if resultado == QDialog.DialogCode.Accepted:
        # Verificar que el usuario autenticado sea admin (doble verificación)
        rol = dialog.get_rol_autenticado()
        if rol == "admin":
            return True
        else:
            QMessageBox.warning(
                parent, "Error de Autenticación",
                "El usuario autenticado no tiene permisos de administrador."
            )
            return False
    
    return False


# Mantener compatibilidad con código antiguo (deprecated)
def solicitar_password(parent=None, accion: str = "realizar esta acción") -> bool:
    """
    Solicita la contraseña de administrador (FUNCIÓN DEPRECADA)
    
    Esta función se mantiene solo para compatibilidad. Se recomienda usar
    solicitar_autenticacion_admin() en su lugar.
    
    Args:
        parent: Widget padre para el diálogo
        accion: Descripción de la acción que requiere autenticación
        
    Returns:
        True si la autenticación es exitosa, False en caso contrario
    """
    return solicitar_autenticacion_admin(parent, accion)

