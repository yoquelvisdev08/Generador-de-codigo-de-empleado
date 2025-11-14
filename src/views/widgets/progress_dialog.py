"""
Diálogo de progreso para operaciones largas
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt6.QtCore import Qt


class ProgressDialog(QDialog):
    """Diálogo que muestra el progreso de una operación"""
    
    def __init__(self, titulo: str = "Procesando...", parent=None):
        """
        Inicializa el diálogo de progreso
        
        Args:
            titulo: Título del diálogo
            parent: Widget padre
        """
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setFixedSize(450, 180)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        self.setLayout(layout)
        
        # Etiqueta de mensaje
        self.label_mensaje = QLabel("Iniciando...")
        self.label_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_mensaje.setWordWrap(True)
        self.label_mensaje.setMinimumHeight(60)
        layout.addWidget(self.label_mensaje)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Botón cancelar (opcional, se puede ocultar)
        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_cancelar.setVisible(False)
        layout.addWidget(self.boton_cancelar)
    
    def actualizar_progreso(self, actual: int, total: int, mensaje: str = ""):
        """
        Actualiza el progreso del diálogo
        
        Args:
            actual: Valor actual
            total: Valor total
            mensaje: Mensaje a mostrar
        """
        if total > 0:
            porcentaje = int((actual / total) * 100)
            self.progress_bar.setValue(porcentaje)
            self.progress_bar.setMaximum(100)
        
        if mensaje:
            self.label_mensaje.setText(mensaje)
        
        # Procesar eventos para actualizar la UI
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
    
    def set_cancelable(self, cancelable: bool):
        """
        Establece si el diálogo puede ser cancelado
        
        Args:
            cancelable: Si True, muestra el botón cancelar
        """
        self.boton_cancelar.setVisible(cancelable)

