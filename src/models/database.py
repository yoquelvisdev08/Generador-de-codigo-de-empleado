"""
Gestión de base de datos SQLite - Optimizada y normalizada
"""
import sqlite3
import random
import shutil
import logging
from datetime import datetime
from typing import Optional, List, Tuple, ContextManager
from pathlib import Path
from contextlib import contextmanager

from config.settings import DB_PATH, BACKUPS_DIR, IMAGES_DIR
from src.utils.constants import ID_CHARACTERS, ID_LENGTH, MAX_ID_GENERATION_ATTEMPTS

# Configurar logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestor de base de datos para códigos de barras - Optimizado"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Inicializa el gestor de base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos. Si es None, usa la ruta por defecto
        """
        self.db_path = db_path or DB_PATH
        self.backups_dir = BACKUPS_DIR
        self.init_database()
        # Limpiar backups antiguos al inicializar (mantener solo los 10 más recientes)
        self.limpiar_backups_antiguos(mantener_ultimos=10)
    
    @contextmanager
    def get_connection(self) -> ContextManager[sqlite3.Connection]:
        """
        Context manager para obtener una conexión a la base de datos
        Cierra automáticamente la conexión al salir del contexto
        
        Yields:
            Conexión SQLite
        """
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=10.0,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
        try:
            yield conn
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Error en base de datos: {e}")
            raise
        finally:
            conn.close()
    
    def init_database(self) -> None:
        """Inicializa la base de datos y crea las tablas necesarias"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Crear tabla principal
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS codigos_barras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_barras TEXT UNIQUE NOT NULL,
                    id_unico TEXT UNIQUE NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    nombre_empleado TEXT,
                    descripcion TEXT,
                    formato TEXT NOT NULL,
                    nombre_archivo TEXT
                )
            """)
            
            # Migraciones: agregar columnas si no existen
            columnas_existentes = self._obtener_columnas_tabla(cursor)
            
            if 'nombre_archivo' not in columnas_existentes:
                try:
                    cursor.execute("ALTER TABLE codigos_barras ADD COLUMN nombre_archivo TEXT")
                except sqlite3.OperationalError:
                    pass
            
            if 'nombre_empleado' not in columnas_existentes:
                try:
                    cursor.execute("ALTER TABLE codigos_barras ADD COLUMN nombre_empleado TEXT")
                except sqlite3.OperationalError:
                    pass
            
            # Crear índices para mejorar el rendimiento
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_codigo_barras 
                ON codigos_barras(codigo_barras)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_id_unico 
                ON codigos_barras(id_unico)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fecha_creacion 
                ON codigos_barras(fecha_creacion DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_nombre_empleado 
                ON codigos_barras(nombre_empleado)
            """)
            
            conn.commit()
            logger.info("Base de datos inicializada correctamente")
    
    def _obtener_columnas_tabla(self, cursor: sqlite3.Cursor) -> List[str]:
        """
        Obtiene la lista de columnas de la tabla codigos_barras
        
        Args:
            cursor: Cursor de la base de datos
            
        Returns:
            Lista de nombres de columnas
        """
        cursor.execute("PRAGMA table_info(codigos_barras)")
        return [row[1] for row in cursor.fetchall()]
    
    def crear_backup_automatico(self, razon: str = "operacion_critica") -> Optional[Path]:
        """
        Crea un backup automático de la base de datos
        
        Args:
            razon: Razón del backup (para el nombre del archivo)
            
        Returns:
            Path del archivo de backup creado, None si falla
        """
        if not self.db_path.exists():
            logger.warning("No se puede crear backup: la base de datos no existe")
            return None
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_backup = f"backup_{razon}_{timestamp}.db"
            ruta_backup = self.backups_dir / nombre_backup
            
            shutil.copy2(str(self.db_path), str(ruta_backup))
            logger.info(f"Backup automático creado: {ruta_backup.name}")
            return ruta_backup
        except Exception as e:
            logger.error(f"Error al crear backup automático: {e}")
            return None
    
    def verificar_codigo_existe(self, codigo_barras: str) -> bool:
        """
        Verifica si un código de barras ya existe
        
        Args:
            codigo_barras: Código de barras a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM codigos_barras WHERE codigo_barras = ? LIMIT 1",
                (codigo_barras,)
            )
            return cursor.fetchone() is not None
    
    def verificar_id_unico_existe(self, id_unico: str) -> bool:
        """
        Verifica si un ID único ya existe
        
        Args:
            id_unico: ID único a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM codigos_barras WHERE id_unico = ? LIMIT 1",
                (id_unico,)
            )
            return cursor.fetchone() is not None
    
    def verificar_existe(self, codigo_barras: Optional[str] = None, 
                        id_unico: Optional[str] = None) -> bool:
        """
        Verifica si existe un código o ID único (método optimizado)
        
        Args:
            codigo_barras: Código de barras a verificar
            id_unico: ID único a verificar
            
        Returns:
            True si existe alguno de los dos, False en caso contrario
        """
        if not codigo_barras and not id_unico:
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if codigo_barras and id_unico:
                cursor.execute(
                    "SELECT 1 FROM codigos_barras WHERE codigo_barras = ? OR id_unico = ? LIMIT 1",
                    (codigo_barras, id_unico)
                )
            elif codigo_barras:
                cursor.execute(
                    "SELECT 1 FROM codigos_barras WHERE codigo_barras = ? LIMIT 1",
                    (codigo_barras,)
                )
            else:
                cursor.execute(
                    "SELECT 1 FROM codigos_barras WHERE id_unico = ? LIMIT 1",
                    (id_unico,)
                )
            
            return cursor.fetchone() is not None
    
    def insertar_codigo(self, codigo_barras: str, id_unico: str, 
                       formato: str, nombre_empleado: Optional[str] = None,
                       descripcion: Optional[str] = None,
                       nombre_archivo: Optional[str] = None) -> bool:
        """
        Inserta un nuevo código de barras en la base de datos
        
        Args:
            codigo_barras: Código de barras
            id_unico: ID único del código
            formato: Formato del código (Code128, EAN13, etc.)
            nombre_empleado: Nombre del empleado (opcional)
            descripcion: Descripción (opcional)
            nombre_archivo: Nombre del archivo de imagen (opcional)
            
        Returns:
            True si se insertó correctamente, False en caso contrario
        """
        # Verificación optimizada en una sola consulta
        if self.verificar_existe(codigo_barras=codigo_barras, id_unico=id_unico):
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO codigos_barras 
                    (codigo_barras, id_unico, formato, nombre_empleado, descripcion, nombre_archivo)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (codigo_barras, id_unico, formato, nombre_empleado, descripcion, nombre_archivo))
                
                conn.commit()
                logger.info(f"Código insertado: {id_unico}")
                return True
            except sqlite3.IntegrityError as e:
                logger.warning(f"Error de integridad al insertar código: {e}")
                conn.rollback()
                return False
    
    def obtener_todos_codigos(self) -> List[Tuple]:
        """
        Obtiene todos los códigos de barras ordenados por fecha de creación
        
        Returns:
            Lista de tuplas con los datos de los códigos
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, codigo_barras, id_unico, fecha_creacion, 
                       nombre_empleado, descripcion, formato, nombre_archivo
                FROM codigos_barras
                ORDER BY fecha_creacion DESC
            """)
            return cursor.fetchall()
    
    def eliminar_codigo(self, codigo_id: int, eliminar_imagen: bool = True) -> bool:
        """
        Elimina un código de barras por su ID
        Crea backup automático antes de eliminar
        
        Args:
            codigo_id: ID del código a eliminar
            eliminar_imagen: Si True, elimina también la imagen asociada
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        # Obtener información del código antes de eliminarlo
        nombre_archivo = None
        if eliminar_imagen:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT nombre_archivo FROM codigos_barras WHERE id = ?",
                    (codigo_id,)
                )
                resultado = cursor.fetchone()
                if resultado:
                    nombre_archivo = resultado[0]
        
        # Crear backup automático antes de eliminar
        self.crear_backup_automatico(f"antes_eliminar_id_{codigo_id}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM codigos_barras WHERE id = ?", (codigo_id,))
            filas_afectadas = cursor.rowcount
            conn.commit()
            
            if filas_afectadas > 0:
                logger.info(f"Código eliminado: ID {codigo_id}")
                
                # Eliminar imagen si existe y se solicitó
                if eliminar_imagen and nombre_archivo:
                    ruta_imagen = IMAGES_DIR / nombre_archivo
                    if ruta_imagen.exists():
                        try:
                            ruta_imagen.unlink()
                            logger.info(f"Imagen eliminada: {nombre_archivo}")
                        except Exception as e:
                            logger.warning(f"No se pudo eliminar la imagen {nombre_archivo}: {e}")
            
            return filas_afectadas > 0
    
    def buscar_codigo(self, termino: str) -> List[Tuple]:
        """
        Busca códigos de barras por término de búsqueda
        
        Args:
            termino: Término de búsqueda
            
        Returns:
            Lista de tuplas con los códigos que coinciden
        """
        termino_busqueda = f"%{termino}%"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, codigo_barras, id_unico, fecha_creacion, 
                       nombre_empleado, descripcion, formato, nombre_archivo
                FROM codigos_barras
                WHERE codigo_barras LIKE ? 
                   OR id_unico LIKE ? 
                   OR nombre_empleado LIKE ? 
                   OR descripcion LIKE ?  -- Código de empleado
                ORDER BY fecha_creacion DESC
            """, (termino_busqueda, termino_busqueda, termino_busqueda, termino_busqueda))
            
            return cursor.fetchall()
    
    def generar_id_aleatorio(self) -> str:
        """
        Genera un ID aleatorio alfanumérico
        
        Returns:
            ID aleatorio de 6 caracteres
        """
        return ''.join(random.choices(ID_CHARACTERS, k=ID_LENGTH))
    
    def obtener_id_aleatorio(self) -> str:
        """
        Obtiene un ID aleatorio único que no existe en la base de datos
        
        Returns:
            ID aleatorio único
            
        Raises:
            Exception: Si no se puede generar un ID único después de múltiples intentos
        """
        intentos = 0
        
        while intentos < MAX_ID_GENERATION_ATTEMPTS:
            id_generado = self.generar_id_aleatorio()
            
            if not self.verificar_codigo_existe(id_generado):
                return id_generado
            
            intentos += 1
        
        raise Exception("No se pudo generar un ID único después de múltiples intentos")
    
    def obtener_siguiente_id_secuencial(self) -> str:
        """
        Obtiene el siguiente ID único disponible (alias de obtener_id_aleatorio)
        
        Returns:
            ID único disponible
        """
        return self.obtener_id_aleatorio()
    
    def obtener_estadisticas(self) -> dict:
        """
        Obtiene estadísticas de la base de datos (optimizado en una sola consulta)
        
        Returns:
            Diccionario con estadísticas (total_codigos, formatos_diferentes)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener ambas estadísticas en una sola consulta
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_codigos,
                    COUNT(DISTINCT formato) as formatos_diferentes
                FROM codigos_barras
            """)
            
            resultado = cursor.fetchone()
            return {
                "total_codigos": resultado[0],
                "formatos_diferentes": resultado[1]
            }
    
    def limpiar_base_datos(self, eliminar_imagenes: bool = True) -> bool:
        """
        Elimina todos los códigos de la base de datos
        Crea backup automático antes de limpiar
        
        Args:
            eliminar_imagenes: Si True, elimina también todas las imágenes asociadas
            
        Returns:
            True si se limpió correctamente, False en caso contrario
        """
        # Crear backup automático antes de limpiar
        backup_path = self.crear_backup_automatico("antes_limpiar_todo")
        
        if not backup_path:
            logger.error("No se pudo crear backup antes de limpiar la base de datos")
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Si se deben eliminar imágenes, obtener lista de archivos primero
                archivos_a_eliminar = []
                if eliminar_imagenes:
                    cursor.execute("SELECT nombre_archivo FROM codigos_barras WHERE nombre_archivo IS NOT NULL")
                    archivos_a_eliminar = [row[0] for row in cursor.fetchall() if row[0]]
                
                cursor.execute("DELETE FROM codigos_barras")
                filas_eliminadas = cursor.rowcount
                conn.commit()
                
                # Eliminar imágenes asociadas
                if eliminar_imagenes and archivos_a_eliminar:
                    eliminadas = 0
                    for nombre_archivo in archivos_a_eliminar:
                        ruta_imagen = IMAGES_DIR / nombre_archivo
                        if ruta_imagen.exists():
                            try:
                                ruta_imagen.unlink()
                                eliminadas += 1
                            except Exception as e:
                                logger.warning(f"No se pudo eliminar {nombre_archivo}: {e}")
                    logger.info(f"Imágenes eliminadas: {eliminadas}/{len(archivos_a_eliminar)}")
                
                logger.info(f"Base de datos limpiada: {filas_eliminadas} registros eliminados")
                return True
            except Exception as e:
                logger.error(f"Error al limpiar base de datos: {e}")
                conn.rollback()
                return False
    
    def obtener_backups_disponibles(self) -> List[Path]:
        """
        Obtiene la lista de backups disponibles
        
        Returns:
            Lista de paths de backups ordenados por fecha (más reciente primero)
        """
        if not self.backups_dir.exists():
            return []
        
        backups = sorted(
            self.backups_dir.glob("backup_*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        return backups
    
    def limpiar_backups_antiguos(self, mantener_ultimos: int = 10) -> int:
        """
        Limpia backups antiguos, manteniendo solo los más recientes
        
        Args:
            mantener_ultimos: Número de backups a mantener
            
        Returns:
            Número de backups eliminados
        """
        backups = self.obtener_backups_disponibles()
        
        if len(backups) <= mantener_ultimos:
            return 0
        
        backups_a_eliminar = backups[mantener_ultimos:]
        eliminados = 0
        
        for backup in backups_a_eliminar:
            try:
                backup.unlink()
                eliminados += 1
                logger.info(f"Backup antiguo eliminado: {backup.name}")
            except Exception as e:
                logger.error(f"Error al eliminar backup {backup.name}: {e}")
        
        return eliminados
    
    def obtener_archivos_imagenes_bd(self) -> set:
        """
        Obtiene el conjunto de nombres de archivos de imágenes que están en la BD
        
        Returns:
            Set con los nombres de archivos de imágenes registradas en la BD
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre_archivo FROM codigos_barras WHERE nombre_archivo IS NOT NULL")
            return {row[0] for row in cursor.fetchall() if row[0]}
    
    def limpiar_imagenes_huerfanas(self) -> Tuple[int, int]:
        """
        Limpia imágenes huérfanas (imágenes que no tienen registro en la BD)
        
        Returns:
            Tupla con (imagenes_eliminadas, errores)
        """
        if not IMAGES_DIR.exists():
            return 0, 0
        
        # Obtener archivos de imágenes en la BD
        archivos_bd = self.obtener_archivos_imagenes_bd()
        
        # Obtener todos los archivos PNG en el directorio
        archivos_directorio = set(IMAGES_DIR.glob("*.png"))
        nombres_archivos_directorio = {archivo.name for archivo in archivos_directorio}
        
        # Encontrar imágenes huérfanas (están en el directorio pero no en la BD)
        imagenes_huerfanas = nombres_archivos_directorio - archivos_bd
        
        eliminadas = 0
        errores = 0
        
        for nombre_archivo in imagenes_huerfanas:
            ruta_imagen = IMAGES_DIR / nombre_archivo
            try:
                ruta_imagen.unlink()
                eliminadas += 1
                logger.info(f"Imagen huérfana eliminada: {nombre_archivo}")
            except Exception as e:
                errores += 1
                logger.error(f"Error al eliminar imagen huérfana {nombre_archivo}: {e}")
        
        return eliminadas, errores
