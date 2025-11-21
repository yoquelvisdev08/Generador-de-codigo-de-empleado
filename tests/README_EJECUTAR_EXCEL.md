# Cómo Ejecutar generar_excel_prueba.py

Este script genera un archivo Excel de prueba con datos de empleados para importar en la aplicación.

## Requisitos

- Python 3.12
- Entorno virtual activado (`env312`)
- Librería `openpyxl` instalada (ya debería estar en requirements.txt)

## Opciones de Ejecución

### Opción 1: Con valores por defecto (2000 registros)

```powershell
# Activar entorno virtual
.\env312\Scripts\Activate.ps1

# Ejecutar script
python tests\generar_excel_prueba.py
```

### Opción 2: Especificar cantidad de registros

```powershell
# Activar entorno virtual
.\env312\Scripts\Activate.ps1

# Generar 500 registros
python tests\generar_excel_prueba.py 500

# Generar 1000 registros
python tests\generar_excel_prueba.py 1000

# Generar 5000 registros
python tests\generar_excel_prueba.py 5000
```

### Opción 3: Especificar cantidad y ruta de guardado

```powershell
# Activar entorno virtual
.\env312\Scripts\Activate.ps1

# Generar 2000 registros y guardar en ruta específica
python tests\generar_excel_prueba.py 2000 "C:\Users\yoquelvis\Desktop\mi_excel_prueba.xlsx"
```

## Ejemplo Completo

```powershell
# 1. Navegar al directorio del proyecto (si no estás ahí)
cd C:\Users\yoquelvis\Desktop\Generador-de-codigo-de-empleado

# 2. Activar entorno virtual
.\env312\Scripts\Activate.ps1

# 3. Ejecutar script (generará 2000 registros por defecto)
python tests\generar_excel_prueba.py

# 4. El script te pedirá dónde guardar el archivo
#    Puedes presionar Enter para usar la ruta sugerida
#    O escribir una ruta completa
```

## Características del Excel Generado

- **Columnas**:
  - Nombre del Empleado (obligatorio)
  - Código de Empleado (obligatorio, formato: EMP00001, EMP00002, etc.)
  - Formato (opcional: Code128, EAN13, EAN8, Code39)

- **Distribución**:
  - ~60% de registros con formato especificado
  - ~40% de registros sin formato (se usará el formato por defecto)

- **Nombres**: Genera nombres realistas de empleados colombianos

## Notas

- Si no especificas una ruta, el script te preguntará dónde guardarlo
- El nombre del archivo incluirá un timestamp automático
- El archivo se puede importar directamente en la aplicación usando la función de importar Excel

