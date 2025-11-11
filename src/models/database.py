"""
Gestión de base de datos SQLite
"""
import sqlite3
import random
from typing import Optional, List, Tuple
from pathlib import Path
from config.settings import DB_PATH
from src.utils.constants import ID_CHARACTERS, ID_LENGTH, MAX_ID_GENERATION_ATTEMPTS


class DatabaseManager:
    """Gestor de base de datos para códigos de barras"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Inicializa el gestor de base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos. Si es None, usa la ruta por defecto
        """
        self.db_path = db_path or DB_PATH
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Obtiene una conexión a la base de datos
        
        Returns:
            Conexión SQLite
        """
        return sqlite3.connect(str(self.db_path))
    
    def init_database(self) -> None:
        """Inicializa la base de datos y crea las tablas necesarias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
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
        try:
            cursor.execute("ALTER TABLE codigos_barras ADD COLUMN nombre_archivo TEXT")
        except sqlite3.OperationalError:
            pass
        
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
        
        conn.commit()
        conn.close()
    
    def verificar_codigo_existe(self, codigo_barras: str) -> bool:
        """
        Verifica si un código de barras ya existe
        
        Args:
            codigo_barras: Código de barras a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM codigos_barras WHERE codigo_barras = ?",
            (codigo_barras,)
        )
        
        resultado = cursor.fetchone()[0] > 0
        conn.close()
        
        return resultado
    
    def verificar_id_unico_existe(self, id_unico: str) -> bool:
        """
        Verifica si un ID único ya existe
        
        Args:
            id_unico: ID único a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM codigos_barras WHERE id_unico = ?",
            (id_unico,)
        )
        
        resultado = cursor.fetchone()[0] > 0
        conn.close()
        
        return resultado
    
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
        if self.verificar_codigo_existe(codigo_barras):
            return False
        
        if self.verificar_id_unico_existe(id_unico):
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO codigos_barras 
                (codigo_barras, id_unico, formato, nombre_empleado, descripcion, nombre_archivo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (codigo_barras, id_unico, formato, nombre_empleado, descripcion, nombre_archivo))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    def obtener_todos_codigos(self) -> List[Tuple]:
        """
        Obtiene todos los códigos de barras ordenados por fecha de creación
        
        Returns:
            Lista de tuplas con los datos de los códigos
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, codigo_barras, id_unico, fecha_creacion, 
                   nombre_empleado, descripcion, formato, nombre_archivo
            FROM codigos_barras
            ORDER BY fecha_creacion DESC
        """)
        
        resultados = cursor.fetchall()
        conn.close()
        
        return resultados
    
    def eliminar_codigo(self, codigo_id: int) -> bool:
        """
        Elimina un código de barras por su ID
        
        Args:
            codigo_id: ID del código a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM codigos_barras WHERE id = ?", (codigo_id,))
        
        filas_afectadas = cursor.rowcount
        conn.commit()
        conn.close()
        
        return filas_afectadas > 0
    
    def buscar_codigo(self, termino: str) -> List[Tuple]:
        """
        Busca códigos de barras por término de búsqueda
        
        Args:
            termino: Término de búsqueda
            
        Returns:
            Lista de tuplas con los códigos que coinciden
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        termino_busqueda = f"%{termino}%"
        cursor.execute("""
            SELECT id, codigo_barras, id_unico, fecha_creacion, 
                   nombre_empleado, descripcion, formato, nombre_archivo
            FROM codigos_barras
            WHERE codigo_barras LIKE ? OR id_unico LIKE ? OR nombre_empleado LIKE ? OR descripcion LIKE ?
            ORDER BY fecha_creacion DESC
        """, (termino_busqueda, termino_busqueda, termino_busqueda, termino_busqueda))
        
        resultados = cursor.fetchall()
        conn.close()
        
        return resultados
    
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
        Obtiene estadísticas de la base de datos
        
        Returns:
            Diccionario con estadísticas (total_codigos, formatos_diferentes)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM codigos_barras")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(DISTINCT formato) FROM codigos_barras
        """)
        formatos = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_codigos": total,
            "formatos_diferentes": formatos
        }
    
    def limpiar_base_datos(self) -> bool:
        """
        Elimina todos los códigos de la base de datos
        
        Returns:
            True si se limpió correctamente, False en caso contrario
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM codigos_barras")
            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False

