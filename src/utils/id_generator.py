"""
Generador de IDs personalizados para códigos de barras
"""
import random
import string
from typing import Optional


class IDGenerator:
    """Generador de IDs personalizados según configuración"""
    
    # Tipos de caracteres disponibles
    TIPO_ALFANUMERICO = "alfanumerico"
    TIPO_NUMERICO = "numerico"
    TIPO_SOLO_LETRAS = "solo_letras"
    
    CARACTERES_ALFANUMERICOS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    CARACTERES_NUMERICOS = "0123456789"
    CARACTERES_SOLO_LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    @classmethod
    def obtener_caracteres_por_tipo(cls, tipo: str) -> str:
        """
        Obtiene los caracteres permitidos según el tipo
        
        Args:
            tipo: Tipo de caracteres (alfanumerico, numerico, solo_letras)
            
        Returns:
            String con los caracteres permitidos
        """
        tipos = {
            cls.TIPO_ALFANUMERICO: cls.CARACTERES_ALFANUMERICOS,
            cls.TIPO_NUMERICO: cls.CARACTERES_NUMERICOS,
            cls.TIPO_SOLO_LETRAS: cls.CARACTERES_SOLO_LETRAS
        }
        return tipos.get(tipo, cls.CARACTERES_ALFANUMERICOS)
    
    @classmethod
    def generar_id_personalizado(
        cls,
        tipo: str = TIPO_ALFANUMERICO,
        longitud: int = 6,
        incluir_nombre: bool = False,
        nombre_empleado: Optional[str] = None,
        verificar_duplicado: Optional[callable] = None
    ) -> str:
        """
        Genera un ID personalizado según las opciones
        
        Args:
            tipo: Tipo de caracteres (alfanumerico, numerico, solo_letras)
            longitud: Longitud del ID
            incluir_nombre: Si True, incluye parte del nombre del empleado
            nombre_empleado: Nombre del empleado (opcional)
            verificar_duplicado: Función para verificar si el ID ya existe
            
        Returns:
            ID generado
        """
        caracteres = cls.obtener_caracteres_por_tipo(tipo)
        
        # Si se debe incluir el nombre
        if incluir_nombre and nombre_empleado:
            nombre_limpio = cls._limpiar_nombre_para_id(nombre_empleado)
            # Tomar las primeras letras del nombre (máximo 3)
            prefijo_nombre = nombre_limpio[:min(3, len(nombre_limpio))].upper()
            # Asegurar que el prefijo solo tenga caracteres válidos
            prefijo_nombre = ''.join(c for c in prefijo_nombre if c in caracteres)
            
            # Calcular cuántos caracteres aleatorios necesitamos
            longitud_aleatoria = max(1, longitud - len(prefijo_nombre))
            parte_aleatoria = ''.join(random.choices(caracteres, k=longitud_aleatoria))
            
            id_generado = prefijo_nombre + parte_aleatoria
        else:
            # Generar ID completamente aleatorio
            id_generado = ''.join(random.choices(caracteres, k=longitud))
        
        # Verificar duplicados si se proporciona la función
        if verificar_duplicado:
            max_intentos = 1000
            intentos = 0
            while verificar_duplicado(id_generado) and intentos < max_intentos:
                if incluir_nombre and nombre_empleado:
                    nombre_limpio = cls._limpiar_nombre_para_id(nombre_empleado)
                    prefijo_nombre = nombre_limpio[:min(3, len(nombre_limpio))].upper()
                    prefijo_nombre = ''.join(c for c in prefijo_nombre if c in caracteres)
                    longitud_aleatoria = max(1, longitud - len(prefijo_nombre))
                    parte_aleatoria = ''.join(random.choices(caracteres, k=longitud_aleatoria))
                    id_generado = prefijo_nombre + parte_aleatoria
                else:
                    id_generado = ''.join(random.choices(caracteres, k=longitud))
                intentos += 1
            
            if intentos >= max_intentos:
                raise Exception("No se pudo generar un ID único después de múltiples intentos")
        
        return id_generado
    
    @classmethod
    def _limpiar_nombre_para_id(cls, nombre: str) -> str:
        """
        Limpia el nombre para usarlo en el ID
        
        Args:
            nombre: Nombre a limpiar
            
        Returns:
            Nombre limpio sin espacios ni caracteres especiales
        """
        # Remover espacios y caracteres especiales, mantener solo letras
        nombre_limpio = ''.join(c for c in nombre if c.isalpha())
        return nombre_limpio.upper()

