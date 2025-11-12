"""
Punto de entrada principal de la aplicación
"""
import sys
import logging
from PyQt6.QtWidgets import QApplication

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
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    controller = MainController()
    controller.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

