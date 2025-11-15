"""
Script para cargar 200 registros de prueba en la base de datos
"""
import random
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.database import DatabaseManager
from src.services.barcode_service import BarcodeService
from src.utils.id_generator import IDGenerator
from config.settings import IMAGES_DIR

# Lista de nombres de empleados para generar datos realistas
NOMBRES_EMPLEADOS = [
    "Juan Pérez", "María González", "Carlos Rodríguez", "Ana Martínez", "Luis Hernández",
    "Laura Sánchez", "Pedro López", "Carmen García", "Miguel Torres", "Sofía Ramírez",
    "Diego Morales", "Elena Fernández", "Roberto Jiménez", "Patricia Ruiz", "Fernando Díaz",
    "Isabel Moreno", "Javier Castro", "Lucía Vargas", "Ricardo Ortega", "Mónica Herrera",
    "Andrés Mendoza", "Gabriela Silva", "Sergio Rojas", "Valentina Medina", "Daniel Vega",
    "Camila Paredes", "Alejandro Campos", "Natalia Guzmán", "Esteban Navarro", "Andrea Fuentes",
    "Felipe Cárdenas", "Mariana Salazar", "Gustavo Peña", "Daniela Ríos", "Héctor Mendoza",
    "Paola Suárez", "Óscar Gutiérrez", "Carolina Méndez", "Jorge Delgado", "Adriana Romero",
    "Manuel Aguilar", "Verónica Cruz", "Raúl Espinoza", "Claudia Ponce", "Eduardo Núñez",
    "Diana Flores", "Mauricio Bravo", "Tatiana Rivas", "Cristian Valdez", "Lorena Córdoba",
    "Sebastián Ochoa", "Angélica Montoya", "Nicolás Restrepo", "Sandra Zapata", "Fabio Quintero",
    "Mónica Arango", "Jhon Jairo", "Yenny López", "Camilo Restrepo", "Diana Carolina",
    "Andrés Felipe", "Sara Milena", "Jorge Mario", "Lina María", "Carlos Andrés",
    "María José", "Juan David", "Laura Sofía", "Santiago", "Valentina",
    "Isabella", "Mateo", "Sofía", "Nicolás", "Mariana",
    "Sebastián", "Daniela", "Samuel", "Valeria", "David",
    "Alejandra", "Julián", "Gabriela", "Camilo", "Paola",
    "Esteban", "Natalia", "Felipe", "Andrea", "Sergio",
    "Carolina", "Andrés", "Diana", "Ricardo", "Mónica",
    "Fernando", "Patricia", "Roberto", "Elena", "Diego",
    "Lucía", "Javier", "Isabel", "Miguel", "Carmen",
    "Pedro", "Laura", "Luis", "Ana", "Carlos",
    "María", "Juan", "José", "Francisco", "Antonio",
    "Manuel", "Pedro", "Jesús", "Miguel", "Ángel",
    "Alejandro", "Roberto", "Fernando", "Carlos", "Luis",
    "Jorge", "Ricardo", "Mario", "Eduardo", "Sergio",
    "Andrés", "Felipe", "Camilo", "Sebastián", "Nicolás",
    "David", "Daniel", "Julián", "Samuel", "Esteban",
    "Gustavo", "Óscar", "Raúl", "Mauricio", "Fabio",
    "Héctor", "Jhon", "Cristian", "Felipe", "Andrés",
    "María", "Ana", "Laura", "Carmen", "Patricia",
    "Isabel", "Elena", "Sofía", "Lucía", "Mónica",
    "Carolina", "Diana", "Gabriela", "Natalia", "Valentina",
    "Mariana", "Andrea", "Paola", "Claudia", "Verónica",
    "Adriana", "Tatiana", "Lorena", "Angélica", "Sandra",
    "Mónica", "Yenny", "Diana Carolina", "Lina María", "Sara Milena",
    "María José", "Laura Sofía", "Isabella", "Valeria", "Alejandra"
]

FORMATOS = ["Code128", "EAN13", "EAN8", "Code39"]

def generar_datos_empleado(numero: int) -> dict:
    """
    Genera datos de un empleado de prueba
    
    Args:
        numero: Número secuencial del empleado
        
    Returns:
        Diccionario con los datos del empleado
    """
    nombre = random.choice(NOMBRES_EMPLEADOS)
    formato = random.choice(FORMATOS)
    
    # Generar código según el formato
    if formato == "EAN13":
        # EAN13 requiere exactamente 13 dígitos
        codigo = ''.join(random.choices("0123456789", k=13))
    elif formato == "EAN8":
        # EAN8 requiere exactamente 8 dígitos
        codigo = ''.join(random.choices("0123456789", k=8))
    else:
        # Code128 y Code39 pueden tener caracteres alfanuméricos
        longitud = random.randint(6, 12)
        codigo = ''.join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=longitud))
    
    return {
        "nombre": nombre,
        "formato": formato,
        "codigo": codigo,
        "descripcion": f"EMP{numero:04d}"
    }

def cargar_registros_prueba(cantidad: int = 200):
    """
    Carga registros de prueba en la base de datos
    
    Args:
        cantidad: Número de registros a cargar
    """
    print(f"Iniciando carga de {cantidad} registros de prueba...")
    
    # Inicializar servicios
    db_manager = DatabaseManager()
    barcode_service = BarcodeService()
    
    # Verificar cuántos registros ya existen
    estadisticas = db_manager.obtener_estadisticas()
    registros_existentes = estadisticas["total_codigos"]
    print(f"Registros existentes en la base de datos: {registros_existentes}")
    
    registros_insertados = 0
    registros_fallidos = 0
    
    for i in range(1, cantidad + 1):
        try:
            # Generar datos del empleado
            datos_empleado = generar_datos_empleado(i)
            
            # Generar ID único
            id_unico = IDGenerator.generar_id_personalizado(
                tipo=IDGenerator.TIPO_ALFANUMERICO,
                longitud=6,
                incluir_nombre=True,
                nombre_empleado=datos_empleado["nombre"],
                verificar_duplicado=lambda id: db_manager.verificar_id_unico_existe(id)
            )
            
            # Generar código de barras y su imagen
            codigo_barras, id_unico_generado, ruta_imagen = barcode_service.generar_codigo_barras(
                datos=datos_empleado["codigo"],
                formato=datos_empleado["formato"],
                id_unico=id_unico,
                nombre_empleado=datos_empleado["nombre"]
            )
            
            # Obtener el nombre del archivo
            nombre_archivo = ruta_imagen.name if ruta_imagen.exists() else None
            
            # Insertar en la base de datos
            exito = db_manager.insertar_codigo(
                codigo_barras=codigo_barras,
                id_unico=id_unico_generado,
                formato=datos_empleado["formato"],
                nombre_empleado=datos_empleado["nombre"],
                descripcion=datos_empleado["descripcion"],
                nombre_archivo=nombre_archivo
            )
            
            if exito:
                registros_insertados += 1
                if i % 10 == 0:
                    print(f"Progreso: {i}/{cantidad} registros procesados...")
            else:
                registros_fallidos += 1
                print(f"Advertencia: No se pudo insertar el registro {i} (posible duplicado)")
                
        except Exception as e:
            registros_fallidos += 1
            print(f"Error al procesar registro {i}: {str(e)}")
    
    # Mostrar resumen
    print("\n" + "="*50)
    print("RESUMEN DE CARGA")
    print("="*50)
    print(f"Registros insertados exitosamente: {registros_insertados}")
    print(f"Registros fallidos: {registros_fallidos}")
    
    # Obtener estadísticas finales
    estadisticas_finales = db_manager.obtener_estadisticas()
    print(f"Total de registros en la base de datos: {estadisticas_finales['total_codigos']}")
    print(f"Formatos diferentes: {estadisticas_finales['formatos_diferentes']}")
    print("="*50)

if __name__ == "__main__":
    try:
        cantidad = int(sys.argv[1]) if len(sys.argv) > 1 else 200
        cargar_registros_prueba(cantidad)
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
    except Exception as e:
        print(f"\nError fatal: {str(e)}")
        sys.exit(1)

