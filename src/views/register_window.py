"""
Ventana de registro para crear el primer usuario administrador
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import re

from config.settings import LOGO_PATH, LOGO_ICON_PATH
from src.models.database import DatabaseManager
from src.utils.password_utils import hash_contraseña, formatear_contraseña_hash
from src.utils.user_logger import user_logger


class RegisterWindow(QWidget):
    """Ventana de registro para crear el primer usuario administrador"""
    
    # Señal emitida cuando el registro es exitoso
    # Parámetros: (usuario: str, rol: str)
    registro_exitoso = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        """
        Inicializa la ventana de registro
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.setWindowTitle("Registro - Generador de Códigos de Barras")
        self.setFixedSize(550, 700)
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Establecer ícono de ventana
        if LOGO_ICON_PATH.exists():
            from PyQt6.QtGui import QIcon
            self.setWindowIcon(QIcon(str(LOGO_ICON_PATH)))
        
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Contenedor principal con fondo degradado
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(50, 40, 50, 50)
        container.setLayout(container_layout)
        
        # Logo de la aplicación
        if LOGO_PATH.exists():
            from PyQt6.QtGui import QPixmap
            logo_label = QLabel()
            pixmap = QPixmap(str(LOGO_PATH))
            # Logo más pequeño pero con buena resolución
            scaled_pixmap = pixmap.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_label.setStyleSheet("background: transparent; border: none;")
            logo_label.setScaledContents(False)
            logo_label.setMinimumHeight(90)
            container_layout.addWidget(logo_label, 0, Qt.AlignmentFlag.AlignHCenter)
            
            # Espaciado después del logo
            container_layout.addSpacing(10)
        else:
            # Fallback: Icono visual de emoji si no existe el logo
            icono_label = QLabel("👤")
            icono_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icono_font = QFont()
            icono_font.setPointSize(48)
            icono_label.setFont(icono_font)
            icono_label.setStyleSheet("background: transparent; border: none; margin-bottom: 10px;")
            container_layout.addWidget(icono_label)
        
        # Título
        titulo = QLabel("Registro de Administrador")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_font = QFont()
        titulo_font.setPointSize(28)
        titulo_font.setBold(True)
        titulo_font.setWeight(700)
        titulo.setFont(titulo_font)
        titulo.setStyleSheet("color: #1a1a2e; margin-bottom: 8px; background: transparent; border: none;")
        container_layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel("Complete el formulario para crear su cuenta de administrador")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet("color: #6c757d; font-size: 13pt; margin-bottom: 30px; font-weight: 400; background: transparent; border: none;")
        subtitulo.setWordWrap(True)
        container_layout.addWidget(subtitulo)
        
        # Campo de nombre
        self.campo_nombre = QLineEdit()
        self.campo_nombre.setPlaceholderText("Nombre completo")
        self.campo_nombre.setMinimumHeight(50)
        self.campo_nombre.setStyleSheet(self._get_input_style())
        self.campo_nombre.returnPressed.connect(lambda: self.campo_email.setFocus())
        container_layout.addWidget(self.campo_nombre)
        
        # Espaciado
        spacer1 = QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        container_layout.addItem(spacer1)
        
        # Campo de email
        self.campo_email = QLineEdit()
        self.campo_email.setPlaceholderText("Email")
        self.campo_email.setMinimumHeight(50)
        self.campo_email.setStyleSheet(self._get_input_style())
        self.campo_email.returnPressed.connect(lambda: self.campo_usuario.setFocus())
        container_layout.addWidget(self.campo_email)
        
        # Espaciado
        spacer2 = QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        container_layout.addItem(spacer2)
        
        # Campo de usuario
        self.campo_usuario = QLineEdit()
        self.campo_usuario.setPlaceholderText("Usuario")
        self.campo_usuario.setMinimumHeight(50)
        self.campo_usuario.setStyleSheet(self._get_input_style())
        self.campo_usuario.returnPressed.connect(lambda: self.campo_password.setFocus())
        container_layout.addWidget(self.campo_usuario)
        
        # Espaciado
        spacer3 = QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        container_layout.addItem(spacer3)
        
        # Campo de contraseña
        self.campo_password = QLineEdit()
        self.campo_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.campo_password.setPlaceholderText("Contraseña")
        self.campo_password.setMinimumHeight(50)
        self.campo_password.setStyleSheet(self._get_input_style())
        self.campo_password.returnPressed.connect(lambda: self.campo_confirmar_password.setFocus())
        container_layout.addWidget(self.campo_password)
        
        # Espaciado
        spacer4 = QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        container_layout.addItem(spacer4)
        
        # Campo de confirmar contraseña
        self.campo_confirmar_password = QLineEdit()
        self.campo_confirmar_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.campo_confirmar_password.setPlaceholderText("Confirmar contraseña")
        self.campo_confirmar_password.setMinimumHeight(50)
        self.campo_confirmar_password.setStyleSheet(self._get_input_style())
        self.campo_confirmar_password.returnPressed.connect(self.validar_registro)
        container_layout.addWidget(self.campo_confirmar_password)
        
        # Espaciado
        spacer5 = QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        container_layout.addItem(spacer5)
        
        # Botón de registro
        self.boton_registrar = QPushButton("Registrarse")
        self.boton_registrar.setMinimumHeight(52)
        self.boton_registrar.setStyleSheet(self._get_button_style())
        self.boton_registrar.clicked.connect(self.validar_registro)
        self.boton_registrar.setDefault(True)
        container_layout.addWidget(self.boton_registrar)
        
        # Agregar contenedor al layout principal
        layout.addWidget(container)
        
        # Estilo de la ventana
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f5f7fa, stop:1 #c3cfe2);
            }
        """)
        
        # Enfocar el campo de nombre al iniciar
        self.campo_nombre.setFocus()
    
    def _get_input_style(self) -> str:
        """Retorna el estilo CSS para los campos de entrada"""
        return """
            QLineEdit {
                padding: 14px 18px;
                font-size: 14pt;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                background-color: #ffffff;
                color: #1a1a2e;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background-color: #ffffff;
                outline: none;
            }
            QLineEdit:hover {
                border: 2px solid #b0b0b0;
            }
        """
    
    def _get_button_style(self) -> str:
        """Retorna el estilo CSS para el botón de registro"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-weight: 600;
                padding: 14px 40px;
                border-radius: 12px;
                font-size: 14pt;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #5568d3, stop:1 #6a3d8f);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4a5bc0, stop:1 #5d357d);
            }
        """
    
    def _get_messagebox_style(self) -> str:
        """Retorna el estilo CSS para los QMessageBox sin fondo en texto e icono"""
        return """
            QMessageBox {
                background-color: #ffffff;
                border-radius: 12px;
            }
            QMessageBox QLabel {
                color: #1a1a2e;
                font-size: 14pt;
                font-weight: 500;
                background: transparent;
                border: none;
            }
            QMessageBox QLabel#qt_msgbox_label {
                color: #1a1a2e;
                background: transparent;
                border: none;
            }
            QMessageBox QLabel#qt_msgboxex_icon_label {
                background: transparent !important;
                border: none !important;
            }
            QMessageBox QLabel[objectName="qt_msgboxex_icon_label"] {
                background: transparent !important;
                border: none !important;
            }
            QMessageBox QLabel[objectName^="qt_msgbox"] {
                background: transparent;
                border: none;
            }
            QMessageBox QPushButton {
                background-color: #667eea;
                color: white;
                font-weight: 600;
                padding: 10px 30px;
                border-radius: 8px;
                font-size: 12pt;
                border: none;
                min-width: 120px;
            }
            QMessageBox QPushButton:hover {
                background-color: #5568d3;
            }
            QMessageBox QPushButton:pressed {
                background-color: #4a5bc0;
            }
        """
    
    def _mostrar_advertencia(self, titulo: str, mensaje: str):
        """Muestra un mensaje de advertencia sin fondo en texto e icono"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setStyleSheet(self._get_messagebox_style())
        # Intentar quitar el fondo del icono después de que se muestre
        from PyQt6.QtCore import QTimer
        def quitar_fondo_icono():
            for label in msg_box.findChildren(QLabel):
                if label.pixmap() is not None:
                    label.setStyleSheet("background: transparent; border: none;")
        QTimer.singleShot(10, quitar_fondo_icono)
        msg_box.exec()
    
    def _mostrar_error(self, titulo: str, mensaje: str):
        """Muestra un mensaje de error sin fondo en texto e icono"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setStyleSheet(self._get_messagebox_style())
        # Intentar quitar el fondo del icono después de que se muestre
        from PyQt6.QtCore import QTimer
        def quitar_fondo_icono():
            for label in msg_box.findChildren(QLabel):
                if label.pixmap() is not None:
                    label.setStyleSheet("background: transparent; border: none;")
        QTimer.singleShot(10, quitar_fondo_icono)
        msg_box.exec()
    
    def _mostrar_informacion(self, titulo: str, mensaje: str):
        """Muestra un mensaje de información sin fondo en texto e icono"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setStyleSheet(self._get_messagebox_style())
        # Intentar quitar el fondo del icono después de que se muestre
        from PyQt6.QtCore import QTimer
        def quitar_fondo_icono():
            for label in msg_box.findChildren(QLabel):
                if label.pixmap() is not None:
                    label.setStyleSheet("background: transparent; border: none;")
        QTimer.singleShot(10, quitar_fondo_icono)
        msg_box.exec()
    
    def validar_email(self, email: str) -> bool:
        """
        Valida el formato de un email
        
        Args:
            email: Email a validar
            
        Returns:
            True si el formato es válido, False en caso contrario
        """
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None
    
    def validar_registro(self):
        """Valida y procesa el registro del usuario"""
        nombre = self.campo_nombre.text().strip()
        email = self.campo_email.text().strip()
        usuario = self.campo_usuario.text().strip()
        password = self.campo_password.text()
        confirmar_password = self.campo_confirmar_password.text()
        
        # Validar campos vacíos
        if not nombre:
            self._mostrar_advertencia("Advertencia", "Por favor ingrese su nombre completo")
            self.campo_nombre.setFocus()
            return
        
        if not email:
            self._mostrar_advertencia("Advertencia", "Por favor ingrese su email")
            self.campo_email.setFocus()
            return
        
        if not self.validar_email(email):
            self._mostrar_advertencia("Advertencia", "Por favor ingrese un email válido")
            self.campo_email.setFocus()
            return
        
        if not usuario:
            self._mostrar_advertencia("Advertencia", "Por favor ingrese un nombre de usuario")
            self.campo_usuario.setFocus()
            return
        
        if len(usuario) < 3:
            self._mostrar_advertencia("Advertencia", "El nombre de usuario debe tener al menos 3 caracteres")
            self.campo_usuario.setFocus()
            return
        
        if not password:
            self._mostrar_advertencia("Advertencia", "Por favor ingrese una contraseña")
            self.campo_password.setFocus()
            return
        
        if len(password) < 6:
            self._mostrar_advertencia("Advertencia", "La contraseña debe tener al menos 6 caracteres")
            self.campo_password.setFocus()
            return
        
        if password != confirmar_password:
            self._mostrar_advertencia("Advertencia", "Las contraseñas no coinciden")
            self.campo_confirmar_password.clear()
            self.campo_confirmar_password.setFocus()
            return
        
        # Verificar si el usuario ya existe
        if self.db_manager.existe_usuario(usuario):
            self._mostrar_error("Error", "El nombre de usuario ya está en uso. Por favor elija otro.")
            self.campo_usuario.clear()
            self.campo_usuario.setFocus()
            return
        
        # Verificar si el email ya existe
        if self.db_manager.existe_email(email):
            self._mostrar_error("Error", "El email ya está registrado. Por favor use otro email.")
            self.campo_email.clear()
            self.campo_email.setFocus()
            return
        
        # Generar hash de la contraseña
        hash_hex, salt = hash_contraseña(password)
        contraseña_hash = formatear_contraseña_hash(hash_hex, salt)
        
        # Crear usuario (siempre como admin en el registro inicial)
        exito = self.db_manager.crear_usuario(
            nombre=nombre,
            email=email,
            usuario=usuario,
            contraseña_hash=contraseña_hash,
            rol="admin"
        )
        
        if exito:
            # Registrar acción
            user_logger.log_registro(usuario, nombre)
            
            self._mostrar_informacion(
                "Registro Exitoso",
                f"Usuario {usuario} registrado correctamente como administrador."
            )
            self.registro_exitoso.emit(usuario, "admin")
            self.close()
        else:
            self._mostrar_error(
                "Error",
                "No se pudo crear el usuario. Por favor intente nuevamente."
            )
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana"""
        # Si se cierra sin registro exitoso, cerrar la aplicación
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().quit()
        event.accept()

