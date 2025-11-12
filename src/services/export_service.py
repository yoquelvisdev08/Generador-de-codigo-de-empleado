"""
Servicio para exportación de códigos de barras
"""
import zipfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

from config.settings import IMAGES_DIR, DB_PATH
from src.utils.file_utils import obtener_ruta_imagen


class ExportService:
    """Servicio para exportar códigos de barras"""
    
    def __init__(self, directorio_imagenes: Optional[Path] = None):
        """
        Inicializa el servicio de exportación
        
        Args:
            directorio_imagenes: Directorio donde están las imágenes. 
                                Si es None, usa el directorio por defecto
        """
        self.directorio_imagenes = directorio_imagenes or IMAGES_DIR
    
    def exportar_seleccionados(self, codigos: List[Tuple], directorio_destino: Path) -> Tuple[int, int]:
        """
        Exporta códigos seleccionados a un directorio
        
        Args:
            codigos: Lista de tuplas con (id_db, codigo_barras, id_unico, formato, nombre_empleado, nombre_archivo)
                     o (id_db, codigo_barras, id_unico, formato, nombre_empleado) para compatibilidad
            directorio_destino: Directorio donde se exportarán los archivos
            
        Returns:
            Tupla con (archivos_exportados, errores)
        """
        exportados = 0
        errores = 0
        
        for codigo in codigos:
            # Compatibilidad con formato anterior (5 elementos) y nuevo (6 elementos)
            if len(codigo) >= 6:
                id_db, codigo_barras, id_unico, formato, nombre_empleado, nombre_archivo = codigo[:6]
            else:
                id_db, codigo_barras, id_unico, formato, nombre_empleado = codigo[:5]
                nombre_archivo = None
            
            # Si tenemos nombre_archivo, usarlo directamente
            if nombre_archivo:
                ruta_imagen = self.directorio_imagenes / nombre_archivo
            else:
                # Fallback: generar ruta como antes
                ruta_imagen = obtener_ruta_imagen(
                    nombre_empleado or "sin_nombre",
                    codigo_barras,
                    self.directorio_imagenes
                )
            
            if not ruta_imagen.exists():
                errores += 1
                continue
            
            ruta_destino = directorio_destino / ruta_imagen.name
            
            try:
                shutil.copy2(str(ruta_imagen), str(ruta_destino))
                exportados += 1
            except Exception:
                errores += 1
        
        return exportados, errores
    
    def exportar_todos_zip(self, codigos: List[Tuple], ruta_zip: Path) -> Tuple[int, int]:
        """
        Exporta todos los códigos a un archivo ZIP
        
        Args:
            codigos: Lista de tuplas con los datos de los códigos
            ruta_zip: Ruta donde se guardará el archivo ZIP
            
        Returns:
            Tupla con (archivos_agregados, errores)
        """
        agregados = 0
        errores = 0
        
        try:
            with zipfile.ZipFile(str(ruta_zip), 'w', zipfile.ZIP_DEFLATED) as zipf:
                for codigo in codigos:
                    if len(codigo) == 8:
                        id_db, codigo_barras, id_unico, fecha, nombre_empleado, descripcion, formato, nombre_archivo_db = codigo
                    else:
                        id_db, codigo_barras, id_unico, fecha, nombre_empleado, descripcion, formato = codigo
                        nombre_archivo_db = obtener_ruta_imagen(
                            nombre_empleado or "sin_nombre",
                            codigo_barras,
                            self.directorio_imagenes
                        ).name
                    
                    ruta_imagen = self.directorio_imagenes / nombre_archivo_db
                    
                    if ruta_imagen.exists():
                        zipf.write(str(ruta_imagen), nombre_archivo_db)
                        agregados += 1
                    else:
                        errores += 1
            
            return agregados, errores
        except Exception:
            return 0, len(codigos)
    
    def crear_backup_base_datos(self, ruta_backup: Path) -> bool:
        """
        Crea un backup de la base de datos
        
        Args:
            ruta_backup: Ruta donde se guardará el backup
            
        Returns:
            True si se creó correctamente, False en caso contrario
        """
        try:
            if DB_PATH.exists():
                shutil.copy2(str(DB_PATH), str(ruta_backup))
                return True
            return False
        except Exception:
            return False
    
    def generar_nombre_backup(self) -> str:
        """
        Genera un nombre de archivo para el backup con timestamp
        
        Returns:
            Nombre del archivo de backup
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"codigos_barras_backup_{timestamp}.db"
    
    def generar_nombre_zip(self) -> str:
        """
        Genera un nombre de archivo ZIP con timestamp
        
        Returns:
            Nombre del archivo ZIP
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"codigos_barras_{timestamp}.zip"

