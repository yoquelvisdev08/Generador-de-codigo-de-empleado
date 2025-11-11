import sqlite3
import os
import random
from datetime import datetime
from typing import Optional, List, Tuple


class DatabaseManager:
    def __init__(self, db_path: str = "codigos_barras.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
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
        
        try:
            cursor.execute("ALTER TABLE codigos_barras ADD COLUMN nombre_archivo TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE codigos_barras ADD COLUMN nombre_empleado TEXT")
        except sqlite3.OperationalError:
            pass
        
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
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM codigos_barras WHERE id = ?", (codigo_id,))
        
        filas_afectadas = cursor.rowcount
        conn.commit()
        conn.close()
        
        return filas_afectadas > 0
    
    def buscar_codigo(self, termino: str) -> List[Tuple]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, codigo_barras, id_unico, fecha_creacion, 
                   nombre_empleado, descripcion, formato, nombre_archivo
            FROM codigos_barras
            WHERE codigo_barras LIKE ? OR id_unico LIKE ? OR nombre_empleado LIKE ? OR descripcion LIKE ?
            ORDER BY fecha_creacion DESC
        """, (f"%{termino}%", f"%{termino}%", f"%{termino}%", f"%{termino}%"))
        
        resultados = cursor.fetchall()
        conn.close()
        
        return resultados
    
    def obtener_id_aleatorio(self) -> str:
        max_intentos = 1000
        intentos = 0
        
        while intentos < max_intentos:
            id_generado = self.generar_id_aleatorio()
            
            if not self.verificar_codigo_existe(id_generado):
                return id_generado
            
            intentos += 1
        
        raise Exception("No se pudo generar un ID único después de múltiples intentos")
    
    def generar_id_aleatorio(self) -> str:
        caracteres = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        longitud = 6
        
        id_aleatorio = ''.join(random.choices(caracteres, k=longitud))
        return id_aleatorio
    
    def obtener_siguiente_id_secuencial(self) -> str:
        return self.obtener_id_aleatorio()
    
    def obtener_estadisticas(self) -> dict:
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
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM codigos_barras")
            filas_eliminadas = cursor.rowcount
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return False

