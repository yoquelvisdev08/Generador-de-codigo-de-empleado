"""
Ventana de login para acceder a la aplicación
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from config.settings import autenticar_usuario, LOGO_PATH, LOGO_ICON_PATH
from src.models.database import DatabaseManager


class LoginWindow(QWidget):
    """Ventana de login para autenticación"""
    
    # Señal emitida cuando el login es exitoso
    # Parámetros: (usuario: str, rol: str)
    login_exitoso = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        """
        Inicializa la ventana de login
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.setWindowTitle("Acceso al Sistema - Generador de Códigos de Barras")
        self.setFixedSize(550, 550)
        self.init_ui()
        
        # Verificar si hay usuarios en la BD después de que la UI esté lista
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.verificar_usuarios)
    
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
        container_layout.setContentsMargins(50, 50, 50, 50)
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
            icono_label = QLabel("🔐")
            icono_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icono_font = QFont()
            icono_font.setPointSize(48)
            icono_label.setFont(icono_font)
            icono_label.setStyleSheet("background: transparent; border: none; margin-bottom: 10px;")
            container_layout.addWidget(icono_label)
        
        # Título con mejor estilo - sin fondo
        titulo = QLabel("Bienvenido")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_font = QFont()
        titulo_font.setPointSize(32)
        titulo_font.setBold(True)
        titulo_font.setWeight(700)
        titulo.setFont(titulo_font)
        titulo.setStyleSheet("color: #1a1a2e; margin-bottom: 8px; background: transparent; border: none;")
        container_layout.addWidget(titulo)
        
        # Subtítulo - sin fondo
        subtitulo = QLabel("Ingrese sus credenciales para acceder")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet("color: #6c757d; font-size: 14pt; margin-bottom: 40px; font-weight: 400; background: transparent; border: none;")
        container_layout.addWidget(subtitulo)
        
        # Campo de usuario - diseño moderno sin label
        self.campo_usuario = QLineEdit()
        self.campo_usuario.setPlaceholderText("Usuario")
        self.campo_usuario.setMinimumHeight(52)
        self.campo_usuario.setStyleSheet("""
            QLineEdit {
                padding: 12px 18px;
                font-size: 13pt;
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
        """)
        self.campo_usuario.returnPressed.connect(lambda: self.campo_password.setFocus())
        container_layout.addWidget(self.campo_usuario)
        
        # Espaciado entre campos
        spacer_campos = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        container_layout.addItem(spacer_campos)
        
        # Campo de contraseña - diseño moderno sin label
        self.campo_password = QLineEdit()
        self.campo_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.campo_password.setPlaceholderText("Contraseña")
        self.campo_password.setMinimumHeight(52)
        self.campo_password.setStyleSheet("""
            QLineEdit {
                padding: 12px 18px;
                font-size: 13pt;
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
        """)
        self.campo_password.returnPressed.connect(self.validar_login)
        container_layout.addWidget(self.campo_password)
        
        # Espaciado entre campo de contraseña y botones
        spacer_botones = QSpacerItem(20, 35, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        container_layout.addItem(spacer_botones)
        
        # Botones con diseño moderno
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(12)
        
        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_cancelar.setMinimumHeight(52)
        self.boton_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #6c757d;
                font-weight: 600;
                padding: 14px 28px;
                border-radius: 12px;
                font-size: 14pt;
                border: 2px solid #e0e0e0;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border: 2px solid #c0c0c0;
            }
            QPushButton:pressed {
                background-color: #e9ecef;
            }
        """)
        self.boton_cancelar.clicked.connect(self.close)
        
        self.boton_ingresar = QPushButton("Ingresar")
        self.boton_ingresar.setMinimumHeight(52)
        self.boton_ingresar.setStyleSheet("""
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
        """)
        self.boton_ingresar.clicked.connect(self.validar_login)
        self.boton_ingresar.setDefault(True)
        
        layout_botones.addWidget(self.boton_cancelar)
        layout_botones.addWidget(self.boton_ingresar)
        container_layout.addLayout(layout_botones)
        
        # Agregar contenedor al layout principal
        layout.addWidget(container)
        
        # Estilo de la ventana con gradiente moderno
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f5f7fa, stop:1 #c3cfe2);
            }
        """)
        
        # Enfocar el campo de usuario al iniciar
        self.campo_usuario.setFocus()
    
    def verificar_usuarios(self):
        """
        Verifica si hay usuarios en la base de datos.
        Si no hay usuarios, emite señal para mostrar ventana de registro.
        """
        cantidad_usuarios = self.db_manager.contar_usuarios()
        if cantidad_usuarios == 0:
            # No hay usuarios, necesitamos mostrar la ventana de registro
            # Emitir señal especial para indicar que se necesita registro
            self.login_exitoso.emit("__REGISTRO_REQUERIDO__", "")
    
    def validar_login(self):
        """Valida las credenciales ingresadas"""
        usuario_ingresado = self.campo_usuario.text().strip()
        password_ingresada = self.campo_password.text()
        
        if not usuario_ingresado:
            QMessageBox.warning(
                self, "Advertencia",
                "Por favor ingrese su usuario"
            )
            self.campo_usuario.setFocus()
            return
        
        if not password_ingresada:
            QMessageBox.warning(
                self, "Advertencia",
                "Por favor ingrese su contraseña"
            )
            self.campo_password.setFocus()
            return
        
        # Validar credenciales
        es_valido, rol = autenticar_usuario(usuario_ingresado, password_ingresada)
        
        if es_valido:
            self.login_exitoso.emit(usuario_ingresado, rol)
            self.close()
        else:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error de Autenticación")
            msg_box.setText("Usuario o contraseña incorrectos. Por favor intente nuevamente.")
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #ffffff;
                    border-radius: 12px;
                }
                QMessageBox QLabel {
                    color: #dc3545;
                    font-size: 14pt;
                    font-weight: 500;
                }
                QMessageBox QLabel#qt_msgbox_label {
                    color: #dc3545;
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
            """)
            # Intentar quitar el fondo del icono después de que se muestre
            from PyQt6.QtCore import QTimer
            def quitar_fondo_icono():
                for label in msg_box.findChildren(QLabel):
                    if label.pixmap() is not None:
                        label.setStyleSheet("background: transparent; border: none;")
            QTimer.singleShot(10, quitar_fondo_icono)
            msg_box.exec()
            self.campo_usuario.clear()
            self.campo_password.clear()
            self.campo_usuario.setFocus()
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana"""
        # Si se cierra sin login exitoso, cerrar la aplicación
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().quit()
        event.accept()

