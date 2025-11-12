"""
Punto de entrada principal de la aplicación
"""
import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.views.login_window import LoginWindow
from src.controllers.main_controller import MainController

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


def main():
    """Función principal de la aplicación"""
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # Mostrar ventana de login primero
        login_window = LoginWindow()
        
        # Centrar la ventana en la pantalla
        screen = app.primaryScreen().geometry()
        size = login_window.frameGeometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        login_window.move(x, y)
        
        login_window.show()
        login_window.raise_()
        login_window.activateWindow()
        
        # Variable para mantener referencia al controlador
        controller_ref = [None]
        
        # Conectar señal de login exitoso para mostrar la ventana principal
        def on_login_exitoso(usuario: str, rol: str):
            logging.info(f"Login exitoso para usuario: {usuario} con rol: {rol}")
            try:
                # Crear controlador con el rol del usuario
                logging.info("Creando MainController...")
                controller = MainController(usuario=usuario, rol=rol)
                controller_ref[0] = controller  # Guardar referencia
                logging.info("MainController creado exitosamente")
                
                # Mostrar y activar la ventana principal (que está en controller.main_window)
                logging.info("Mostrando ventana principal...")
                
                # Centrar la ventana antes de mostrarla
                controller.main_window._centrar_ventana()
                
                # Asegurar que la ventana esté visible y no minimizada
                controller.main_window.setWindowState(controller.main_window.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
                controller.main_window.show()
                controller.main_window.raise_()
                controller.main_window.activateWindow()
                controller.main_window.setVisible(True)
                
                # Forzar actualización del event loop
                QApplication.instance().processEvents()
                
                logging.info(f"Ventana principal mostrada - Posición: {controller.main_window.pos()}, Tamaño: {controller.main_window.size()}, Visible: {controller.main_window.isVisible()}")
                
                # Cerrar la ventana de login después de mostrar la principal
                login_window.close()
            except Exception as e:
                logging.error(f"Error al mostrar ventana principal: {e}", exc_info=True)
        
        login_window.login_exitoso.connect(on_login_exitoso)
        
        # Modificar el closeEvent de login_window para que no cierre la app si ya hay un controlador
        original_close_event = login_window.closeEvent
        def new_close_event(event):
            if controller_ref[0] is None:
                # Si no hay controlador, cerrar la aplicación
                QApplication.instance().quit()
            else:
                # Si hay controlador, solo cerrar la ventana de login
                event.accept()
        login_window.closeEvent = new_close_event
        
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Error al iniciar la aplicación: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

