"""
Punto de entrada principal de la aplicación
"""
import sys
from PyQt6.QtWidgets import QApplication

from src.controllers.main_controller import MainController


def main():
    """Función principal de la aplicación"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    controller = MainController()
    controller.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

