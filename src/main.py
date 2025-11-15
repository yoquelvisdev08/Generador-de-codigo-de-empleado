"""
Punto de entrada principal de la aplicación
"""
import sys
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from src.views.login_window import LoginWindow
from src.views.register_window import RegisterWindow
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
        
        # Variable para mantener referencia al controlador
        controller_ref = [None]
        
        # Variable para mantener referencia a las ventanas
        current_window_ref = [None]
        
        # Variable para indicar si se está mostrando registro
        mostrando_registro = [False]
        
        def mostrar_ventana_principal(usuario: str, rol: str):
            """Muestra la ventana principal después de login/registro exitoso"""
            logging.info(f"Acceso exitoso para usuario: {usuario} con rol: {rol}")
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
                
                # Cerrar la ventana actual (login o registro)
                if current_window_ref[0]:
                    current_window_ref[0].close()
            except Exception as e:
                logging.error(f"Error al mostrar ventana principal: {e}", exc_info=True)
        
        def on_login_exitoso(usuario: str, rol: str):
            """Maneja el login exitoso o la necesidad de registro"""
            if usuario == "__REGISTRO_REQUERIDO__":
                # No hay usuarios, mostrar ventana de registro
                logging.info("No hay usuarios en la BD, mostrando ventana de registro")
                mostrando_registro[0] = True
                
                try:
                    register_window = RegisterWindow()
                    current_window_ref[0] = register_window
                    
                    # Centrar la ventana en la pantalla
                    screen = app.primaryScreen().geometry()
                    size = register_window.frameGeometry()
                    x = (screen.width() - size.width()) // 2
                    y = (screen.height() - size.height()) // 2
                    register_window.move(x, y)
                    
                    register_window.show()
                    register_window.raise_()
                    register_window.activateWindow()
                    
                    # Conectar señal de registro exitoso
                    def on_registro_exitoso(usuario: str, rol: str):
                        mostrando_registro[0] = False
                        mostrar_ventana_principal(usuario, rol)
                    
                    register_window.registro_exitoso.connect(on_registro_exitoso)
                    
                    # Modificar closeEvent para cerrar app si no hay controlador
                    original_close_event = register_window.closeEvent
                    def new_close_event(event):
                        if controller_ref[0] is None:
                            QApplication.instance().quit()
                        else:
                            event.accept()
                    register_window.closeEvent = new_close_event
                    
                    # Cerrar ventana de login después de mostrar registro
                    login_window.hide()
                except Exception as e:
                    logging.error(f"Error al crear ventana de registro: {e}", exc_info=True)
                    mostrando_registro[0] = False
                    QMessageBox.critical(
                        None, "Error",
                        f"Error al crear ventana de registro: {e}"
                    )
            else:
                # Login exitoso normal
                mostrar_ventana_principal(usuario, rol)
        
        # Mostrar ventana de login primero
        login_window = LoginWindow()
        current_window_ref[0] = login_window
        
        # Centrar la ventana en la pantalla
        screen = app.primaryScreen().geometry()
        size = login_window.frameGeometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        login_window.move(x, y)
        
        login_window.show()
        login_window.raise_()
        login_window.activateWindow()
        
        # Conectar señal de login exitoso
        login_window.login_exitoso.connect(on_login_exitoso)
        
        # Modificar el closeEvent de login_window para que no cierre la app si ya hay un controlador o se está mostrando registro
        original_close_event = login_window.closeEvent
        def new_close_event(event):
            if controller_ref[0] is None and not mostrando_registro[0]:
                # Si no hay controlador y no se está mostrando registro, cerrar la aplicación
                QApplication.instance().quit()
            else:
                # Si hay controlador o se está mostrando registro, solo cerrar la ventana de login
                event.accept()
        login_window.closeEvent = new_close_event
        
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Error al iniciar la aplicación: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

