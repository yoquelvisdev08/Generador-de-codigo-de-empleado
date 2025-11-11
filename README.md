# Generador de Códigos de Barras

Aplicación de escritorio con interfaz gráfica para generar códigos de barras con ID único y gestión mediante base de datos local SQLite.

**by yoquelvisdev**

## Características

- Generación de códigos de barras en múltiples formatos (Code128, EAN13, EAN8, Code39)
- Asignación automática de ID único (UUID) a cada código generado
- Base de datos local SQLite para almacenamiento persistente
- Verificación de duplicados antes de generar nuevos códigos
- Interfaz gráfica moderna y profesional con PyQt6
- Vista previa de códigos generados
- Búsqueda y filtrado de códigos existentes
- Exportación de imágenes de códigos de barras
- Gestión completa de códigos (crear, ver, eliminar)

## Requisitos del Sistema

- Python 3.8 o superior
- Windows, Linux o macOS

### Requisitos Adicionales para macOS

Si está usando macOS, necesitará instalar la librería `zbar` (requerida por `pyzbar` para la lectura de códigos de barras):

```bash
brew install zbar
```

**Nota:** El script de activación del entorno virtual está configurado para configurar automáticamente las variables de entorno necesarias en macOS. Si tiene problemas, asegúrese de que Homebrew esté instalado y que `zbar` esté correctamente instalado.

## Instalación

1. Clonar o descargar el proyecto

2. Crear un entorno virtual (recomendado):

**En Windows (PowerShell):**
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

**En Windows (CMD):**
```cmd
python -m venv env
env\Scripts\activate.bat
```

**En Linux/macOS:**
```bash
python3 -m venv env
source env/bin/activate
```

Si obtiene un error de política de ejecución en PowerShell, ejecute primero:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

3. Instalar las dependencias necesarias:

```bash
pip install -r requirements.txt
```

Las dependencias incluyen:
- PyQt6: Para la interfaz gráfica
- python-barcode: Para generar códigos de barras
- Pillow: Para el procesamiento de imágenes
- pyzbar: Para la lectura y validación de códigos de barras (requiere zbar en macOS)
- numpy: Para el procesamiento de imágenes

## Uso

### Ejecutar la aplicación

**Con el entorno virtual activado:**

```bash
python main.py
```

**Nota:** Asegúrese de tener el entorno virtual activado antes de ejecutar la aplicación. Verá `(env)` al inicio de su línea de comandos cuando esté activado.

**En macOS:** Si obtiene un error relacionado con `zbar`, asegúrese de haber instalado `zbar` con Homebrew (ver requisitos adicionales arriba) y de que el entorno virtual esté activado correctamente. El script de activación configura automáticamente las variables de entorno necesarias.

### Generar un código de barras

1. Ingrese el nombre del empleado en el campo "Nombre del Empleado"
2. Seleccione el formato deseado (Code128, EAN13, EAN8, Code39)
3. Opcionalmente, agregue una descripción
4. Haga clic en "Generar Código de Barras"

El sistema generará automáticamente un ID único aleatorio (alfanumérico de 6 caracteres) que se codificará en el código de barras. El ID aparecerá debajo del código y es el valor que se leerá al escanearlo.

### Formatos de Código de Barras

- **Code128**: Acepta caracteres alfanuméricos (hasta 80 caracteres)
- **EAN13**: Requiere exactamente 13 dígitos numéricos
- **EAN8**: Requiere exactamente 8 dígitos numéricos
- **Code39**: Acepta caracteres alfanuméricos y algunos especiales (hasta 43 caracteres)

### Funcionalidades Adicionales

- **Búsqueda**: Use el campo de búsqueda para filtrar códigos por código de barras, ID único, nombre de empleado o descripción
- **Vista Previa**: Haga doble clic en una fila de la tabla o use el botón "Ver Imagen" para ver la imagen del código
- **Exportar Seleccionados**: Seleccione múltiples códigos (Ctrl+clic o Shift+clic) y exporte las imágenes a una carpeta. Los archivos se nombran como: `nombre_empleado_codigo_barras.png`
- **Exportar Todos (ZIP)**: Exporta todos los códigos en un archivo ZIP con el mismo formato de nombres
- **Backup BD**: Crea un backup de la base de datos con timestamp
- **Eliminar**: Seleccione un código y haga clic en "Eliminar" para removerlo de la base de datos
- **Limpiar Base de Datos**: Elimina todos los códigos de la base de datos (acción irreversible)

## Estructura del Proyecto

```
Codigo-de-barra/
├── main.py                 # Interfaz gráfica principal
├── database.py             # Gestión de base de datos SQLite
├── barcode_generator.py    # Generación de códigos de barras
├── requirements.txt        # Dependencias del proyecto
├── README.md              # Este archivo
├── codigos_barras.db      # Base de datos SQLite (se crea automáticamente)
└── codigos_generados/     # Directorio con imágenes de códigos (se crea automáticamente)
```

## Base de Datos

La aplicación utiliza SQLite como base de datos local. El archivo `codigos_barras.db` se crea automáticamente al ejecutar la aplicación por primera vez.

### Estructura de la Tabla

- `id`: Identificador único del registro (auto-incremental)
- `codigo_barras`: ID único aleatorio alfanumérico codificado en el código de barras
- `id_unico`: ID único aleatorio alfanumérico (mismo que codigo_barras)
- `fecha_creacion`: Timestamp de creación
- `nombre_empleado`: Nombre del empleado asociado al código
- `descripcion`: Descripción opcional del código
- `formato`: Formato del código de barras utilizado (Code128, EAN13, EAN8, Code39)

## Notas Técnicas

- Los códigos de barras se generan como imágenes PNG en el directorio `codigos_generados/`
- Cada código tiene un ID único aleatorio alfanumérico de 6 caracteres (0-9, A-Z) que garantiza la unicidad
- El sistema verifica duplicados antes de generar cada ID, asegurando que no se repitan
- El ID generado es el valor que se codifica en el código de barras y aparece como texto debajo del código
- Al escanear el código de barras, se leerá exactamente ese ID único
- La base de datos incluye índices para optimizar las búsquedas
- Los nombres de archivo exportados siguen el formato: `nombre_empleado_codigo_barras.png`

## Solución de Problemas

### Error al instalar PyQt6

Si tiene problemas instalando PyQt6 en Windows, asegúrese de tener las herramientas de compilación de Python:

```bash
pip install --upgrade pip
pip install PyQt6
```

### Error al generar códigos EAN13/EAN8

Estos formatos requieren exactamente 13 y 8 dígitos respectivamente. Asegúrese de ingresar solo números y la cantidad correcta de dígitos.

### La base de datos no se crea

Verifique que tenga permisos de escritura en el directorio del proyecto.

### Error "Unable to find zbar shared library" en macOS

Este error ocurre cuando `pyzbar` no puede encontrar la librería `zbar`. Solución:

1. Instale `zbar` con Homebrew:
   ```bash
   brew install zbar
   ```

2. Asegúrese de activar el entorno virtual correctamente:
   ```bash
   source env/bin/activate
   ```

3. El script de activación del entorno virtual está configurado para configurar automáticamente las variables de entorno necesarias. Si el problema persiste, puede configurar manualmente:
   ```bash
   export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_FALLBACK_LIBRARY_PATH
   ```

4. Use `python3` en lugar de `python` cuando el entorno virtual esté activado:
   ```bash
   python3 main.py
   ```

## Licencia

Este proyecto es de código abierto y está disponible para uso personal y comercial.

---

**Desarrollado por yoquelvisdev**
