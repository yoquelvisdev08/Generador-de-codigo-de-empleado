"""
Utilidades de autenticación
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from config.settings import ADMIN_PASSWORD


class PasswordDialog(QDialog):
    """Diálogo para solicitar contraseña de administrador"""
    
    def __init__(self, parent=None, accion: str = "realizar esta acción"):
        """
        Inicializa el diálogo de contraseña
        
        Args:
            parent: Widget padre
            accion: Descripción de la acción que requiere autenticación
        """
        super().__init__(parent)
        self.accion = accion
        self.password_correcta = False
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Autenticación Requerida")
        self.setModal(True)
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        label_info = QLabel(
            f"Se requiere contraseña de administrador para {self.accion}.\n"
            "Por favor ingrese la contraseña:"
        )
        label_info.setWordWrap(True)
        layout.addWidget(label_info)
        
        self.campo_password = QLineEdit()
        self.campo_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.campo_password.setPlaceholderText("Ingrese la contraseña")
        self.campo_password.returnPressed.connect(self.verificar_password)
        layout.addWidget(self.campo_password)
        
        layout_botones = QVBoxLayout()
        
        boton_aceptar = QPushButton("Aceptar")
        boton_aceptar.clicked.connect(self.verificar_password)
        boton_aceptar.setDefault(True)
        layout_botones.addWidget(boton_aceptar)
        
        boton_cancelar = QPushButton("Cancelar")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        layout.addLayout(layout_botones)
        
        # Enfocar el campo de contraseña al abrir
        self.campo_password.setFocus()
    
    def verificar_password(self):
        """Verifica si la contraseña ingresada es correcta"""
        password_ingresada = self.campo_password.text()
        
        if password_ingresada == ADMIN_PASSWORD:
            self.password_correcta = True
            self.accept()
        else:
            QMessageBox.warning(
                self, "Contraseña Incorrecta",
                "La contraseña ingresada no es correcta.\n"
                "Por favor intente nuevamente."
            )
            self.campo_password.clear()
            self.campo_password.setFocus()
    
    def is_password_correct(self) -> bool:
        """
        Verifica si la contraseña fue ingresada correctamente
        
        Returns:
            True si la contraseña es correcta, False en caso contrario
        """
        return self.password_correcta


def solicitar_password(parent=None, accion: str = "realizar esta acción") -> bool:
    """
    Solicita la contraseña de administrador
    
    Args:
        parent: Widget padre para el diálogo
        accion: Descripción de la acción que requiere autenticación
        
    Returns:
        True si la contraseña es correcta, False en caso contrario
    """
    dialog = PasswordDialog(parent, accion)
    resultado = dialog.exec()
    return resultado == QDialog.DialogCode.Accepted and dialog.is_password_correct()

