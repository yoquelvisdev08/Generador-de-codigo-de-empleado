"""
Diálogo de progreso para operaciones largas
"""
import time
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
        self.setFixedSize(450, 220)
        
        # Variables para calcular tiempo estimado
        self.tiempo_inicio = time.time()
        self.ultimo_actual = 0
        self.ultimo_tiempo = self.tiempo_inicio
        
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
        
        # Etiqueta de tiempo estimado
        self.label_tiempo_estimado = QLabel("Calculando tiempo estimado...")
        self.label_tiempo_estimado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_tiempo_estimado.setStyleSheet("color: #666; font-size: 10pt;")
        layout.addWidget(self.label_tiempo_estimado)
        
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
        tiempo_actual = time.time()
        
        if total > 0:
            porcentaje = int((actual / total) * 100)
            self.progress_bar.setValue(porcentaje)
            self.progress_bar.setMaximum(100)
            
            # Calcular tiempo estimado
            tiempo_transcurrido = tiempo_actual - self.tiempo_inicio
            
            if actual > 0 and actual > self.ultimo_actual:
                # Calcular velocidad (items por segundo)
                tiempo_delta = tiempo_actual - self.ultimo_tiempo
                items_delta = actual - self.ultimo_actual
                
                if tiempo_delta > 0 and items_delta > 0:
                    velocidad = items_delta / tiempo_delta
                    
                    # Calcular tiempo restante
                    items_restantes = total - actual
                    if velocidad > 0:
                        segundos_restantes = items_restantes / velocidad
                        tiempo_estimado = self._formatear_tiempo(segundos_restantes)
                        tiempo_transcurrido_str = self._formatear_tiempo(tiempo_transcurrido)
                        self.label_tiempo_estimado.setText(
                            f"Tiempo transcurrido: {tiempo_transcurrido_str} | Tiempo estimado restante: {tiempo_estimado}"
                        )
                    else:
                        self.label_tiempo_estimado.setText(
                            f"Tiempo transcurrido: {self._formatear_tiempo(tiempo_transcurrido)} | Calculando..."
                        )
                else:
                    # Si no hay progreso suficiente, usar tiempo transcurrido y porcentaje
                    if porcentaje > 0:
                        tiempo_total_estimado = tiempo_transcurrido / (porcentaje / 100.0)
                        segundos_restantes = tiempo_total_estimado - tiempo_transcurrido
                        if segundos_restantes > 0:
                            tiempo_estimado = self._formatear_tiempo(segundos_restantes)
                            tiempo_transcurrido_str = self._formatear_tiempo(tiempo_transcurrido)
                            self.label_tiempo_estimado.setText(
                                f"Tiempo transcurrido: {tiempo_transcurrido_str} | Tiempo estimado restante: {tiempo_estimado}"
                            )
                        else:
                            self.label_tiempo_estimado.setText(
                                f"Tiempo transcurrido: {self._formatear_tiempo(tiempo_transcurrido)} | Finalizando..."
                            )
                    else:
                        self.label_tiempo_estimado.setText(
                            f"Tiempo transcurrido: {self._formatear_tiempo(tiempo_transcurrido)} | Iniciando..."
                        )
            elif actual == 0:
                self.label_tiempo_estimado.setText("Calculando tiempo estimado...")
            
            # Actualizar valores para próxima iteración
            self.ultimo_actual = actual
            self.ultimo_tiempo = tiempo_actual
        else:
            # Si total es 0, solo mostrar tiempo transcurrido
            tiempo_transcurrido_str = self._formatear_tiempo(tiempo_actual - self.tiempo_inicio)
            self.label_tiempo_estimado.setText(f"Tiempo transcurrido: {tiempo_transcurrido_str}")
        
        if mensaje:
            self.label_mensaje.setText(mensaje)
        
        # Procesar eventos para actualizar la UI
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
    
    def _formatear_tiempo(self, segundos: float) -> str:
        """
        Formatea segundos a formato legible (MM:SS o HH:MM:SS)
        
        Args:
            segundos: Tiempo en segundos
            
        Returns:
            String formateado
        """
        if segundos < 0:
            return "00:00"
        
        segundos = int(segundos)
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segs = segundos % 60
        
        if horas > 0:
            return f"{horas:02d}:{minutos:02d}:{segs:02d}"
        else:
            return f"{minutos:02d}:{segs:02d}"
    
    def set_cancelable(self, cancelable: bool):
        """
        Establece si el diálogo puede ser cancelado
        
        Args:
            cancelable: Si True, muestra el botón cancelar
        """
        self.boton_cancelar.setVisible(cancelable)

