"""
Sistema de logging de acciones de usuarios
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import DATA_DIR

# Directorio para logs de usuarios
LOGS_DIR = DATA_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class UserLogger:
    """Logger para registrar acciones de usuarios"""
    
    def __init__(self):
        """Inicializa el logger de usuarios"""
        self.logs_dir = LOGS_DIR
        
        # Crear logger específico para acciones de usuarios
        self.logger = logging.getLogger('user_actions')
        self.logger.setLevel(logging.INFO)
        
        # Evitar duplicados de handlers
        if not self.logger.handlers:
            # Handler para archivo de log diario
            log_file = self.logs_dir / f"user_actions_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Formato del log
            formatter = logging.Formatter(
                '%(asctime)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
    
    def log_action(self, usuario: str, accion: str, detalles: Optional[str] = None):
        """
        Registra una acción de un usuario
        
        Args:
            usuario: Nombre de usuario que realiza la acción
            accion: Descripción de la acción realizada
            detalles: Detalles adicionales opcionales
        """
        mensaje = f"Usuario: {usuario} | Acción: {accion}"
        if detalles:
            mensaje += f" | Detalles: {detalles}"
        
        self.logger.info(mensaje)
    
    def log_generar_codigo(self, usuario: str, nombre_empleado: str, codigo_empleado: str, formato: str):
        """Registra la generación de un código de barras"""
        detalles = f"Empleado: {nombre_empleado}, Código: {codigo_empleado}, Formato: {formato}"
        self.log_action(usuario, "Generar código de barras", detalles)
    
    def log_eliminar_codigo(self, usuario: str, codigo_id: int):
        """Registra la eliminación de un código de barras"""
        self.log_action(usuario, "Eliminar código de barras", f"ID: {codigo_id}")
    
    def log_exportar_codigos(self, usuario: str, cantidad: int, tipo: str = "seleccionados"):
        """Registra la exportación de códigos"""
        self.log_action(usuario, f"Exportar códigos ({tipo})", f"Cantidad: {cantidad}")
    
    def log_importar_excel(self, usuario: str, cantidad: int, exitosos: int, errores: int):
        """Registra la importación desde Excel"""
        detalles = f"Total: {cantidad}, Exitosos: {exitosos}, Errores: {errores}"
        self.log_action(usuario, "Importar desde Excel", detalles)
    
    def log_exportar_excel(self, usuario: str, cantidad: int):
        """Registra la exportación a Excel"""
        self.log_action(usuario, "Exportar a Excel", f"Cantidad: {cantidad}")
    
    def log_backup(self, usuario: str):
        """Registra la creación de un backup"""
        self.log_action(usuario, "Crear backup de base de datos")
    
    def log_limpiar_bd(self, usuario: str):
        """Registra la limpieza de la base de datos"""
        self.log_action(usuario, "Limpiar base de datos")
    
    def log_limpiar_imagenes(self, usuario: str, cantidad: int):
        """Registra la limpieza de imágenes huérfanas"""
        self.log_action(usuario, "Limpiar imágenes huérfanas", f"Cantidad: {cantidad}")
    
    def log_generar_carnet(self, usuario: str, nombre_empleado: str, tipo: str = "individual"):
        """Registra la generación de un carnet"""
        self.log_action(usuario, f"Generar carnet ({tipo})", f"Empleado: {nombre_empleado}")
    
    def log_generar_carnets_masivos(self, usuario: str, cantidad: int):
        """Registra la generación masiva de carnets"""
        self.log_action(usuario, "Generar carnets masivos", f"Cantidad: {cantidad}")
    
    def log_buscar(self, usuario: str, termino: str):
        """Registra una búsqueda"""
        self.log_action(usuario, "Búsqueda", f"Término: {termino}")
    
    def log_login(self, usuario: str):
        """Registra un inicio de sesión"""
        self.log_action(usuario, "Inicio de sesión")
    
    def log_registro(self, usuario: str, nombre: str):
        """Registra el registro de un nuevo usuario"""
        self.log_action(usuario, "Registro de nuevo usuario", f"Nombre: {nombre}")


# Instancia global del logger
user_logger = UserLogger()

