# Generador de Códigos de Barras

Aplicación de escritorio con interfaz gráfica para generar códigos de barras con ID único y gestión mediante base de datos local SQLite.

**by yoquelvisdev**

## Características

- **Sistema de autenticación**: Login con usuario y contraseña, soporte para roles (admin/user)
- **Generación de códigos de barras**: Múltiples formatos (Code128, EAN13, EAN8, Code39)
- **ID personalizado**: Configuración de tipo de caracteres, longitud e inclusión de nombre
- **Base de datos local SQLite**: Almacenamiento persistente con backups automáticos
- **Verificación de duplicados**: Antes de generar nuevos códigos
- **Interfaz gráfica moderna**: Diseño profesional con PyQt6
- **Vista previa en tiempo real**: Actualización automática del ID mientras configura opciones
- **Búsqueda y filtrado**: Búsqueda avanzada de códigos existentes
- **Exportación**: Exportación individual o masiva de imágenes
- **Editor de Carnets**: Diseño de carnets de identificación con templates HTML
- **Gestión completa**: Crear, ver, eliminar códigos y gestionar imágenes
- **Control de permisos**: Los administradores tienen acceso a funciones adicionales

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
- python-dotenv: Para gestionar variables de entorno y configuración de seguridad

## Uso

### Ejecutar la aplicación

**Con el entorno virtual activado:**

```bash
python main.py
```

O usando el script de ejecución (recomendado):

```bash
./run.sh
```

**Nota:** Asegúrese de tener el entorno virtual activado antes de ejecutar la aplicación. Verá `(env)` al inicio de su línea de comandos cuando esté activado.

**Al iniciar la aplicación:**
1. Se mostrará una ventana de login
2. Ingrese su usuario y contraseña configurados en el archivo `.env`
3. Después del login exitoso, se abrirá la ventana principal de la aplicación

**En macOS:** Si obtiene un error relacionado con `zbar`, asegúrese de haber instalado `zbar` con Homebrew (ver requisitos adicionales arriba) y de que el entorno virtual esté activado correctamente. El script de activación configura automáticamente las variables de entorno necesarias.

### Generar un código de barras

1. Ingrese el nombre del empleado en el campo "Nombre del Empleado"
2. Ingrese el código de empleado en el campo "Código de Empleado" (campo obligatorio)
3. Seleccione el formato deseado (Code128, EAN13, EAN8, Code39)
4. Configure las opciones de generación de ID:
   - Tipo de caracteres: Alfanumérico, Numérico, o Solo Letras
   - Cantidad de caracteres (por defecto: 10)
   - Opcionalmente, incluya el nombre del empleado en el código
5. El ID se generará automáticamente y se mostrará en tiempo real en la vista previa
6. Haga clic en "Generar Código de Barras"

El sistema generará automáticamente un ID único personalizado según las opciones seleccionadas. El ID aparecerá debajo del código y es el valor que se leerá al escanearlo.

### Formatos de Código de Barras

- **Code128**: Acepta caracteres alfanuméricos (hasta 80 caracteres)
- **EAN13**: Requiere exactamente 13 dígitos numéricos
- **EAN8**: Requiere exactamente 8 dígitos numéricos
- **Code39**: Acepta caracteres alfanuméricos y algunos especiales (hasta 43 caracteres)

### Funcionalidades Adicionales

- **Búsqueda**: Use el campo de búsqueda para filtrar códigos por código de barras, ID único, nombre de empleado o código de empleado
- **Vista Previa**: Al seleccionar un código en la tabla, la imagen se muestra automáticamente en el panel de generación
- **Exportar Seleccionados**: Seleccione múltiples códigos (Ctrl+clic o Shift+clic) y exporte las imágenes a una carpeta. Los archivos se nombran como: `nombre_empleado_codigo_barras.png`
- **Exportar Todos (ZIP)**: Exporta todos los códigos en un archivo ZIP con el mismo formato de nombres
- **Crear Carnet**: Botón para acceder al editor de carnets de identificación
- **Backup BD** (Solo Admin): Crea un backup de la base de datos con timestamp
- **Eliminar**: Seleccione un código y haga clic en "Eliminar" para removerlo de la base de datos
- **Limpiar Base de Datos** (Solo Admin): Elimina todos los códigos de la base de datos (acción irreversible)
- **Limpiar Imágenes Huérfanas** (Solo Admin): Elimina imágenes que no tienen registro en la base de datos

## Arquitectura del Proyecto

El proyecto utiliza una arquitectura **MVP (Model-View-Presenter)** que separa claramente las responsabilidades:

- **Models**: Gestión de datos y acceso a la base de datos
- **Views**: Componentes de la interfaz de usuario (ventanas y widgets)
- **Services**: Lógica de negocio (generación de códigos, exportación)
- **Controllers**: Coordinación entre modelos, servicios y vistas
- **Utils**: Utilidades y funciones auxiliares
- **Config**: Configuración centralizada de la aplicación

## Estructura del Proyecto

```
Generador-de-codigo-de-empleado/
├── main.py                    # Punto de entrada principal
├── src/                       # Código fuente principal
│   ├── __init__.py
│   ├── main.py               # Inicialización de la aplicación
│   │
│   ├── models/               # Capa de datos (Model)
│   │   ├── __init__.py
│   │   ├── database.py       # Gestor de base de datos SQLite
│   │   ├── barcode_model.py  # Modelo de datos para códigos
│   │   ├── html_template.py  # Modelo de templates HTML
│   │   └── carnet_template.py # Modelo de templates de carnet
│   │
│   ├── services/             # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── barcode_service.py    # Generación y validación de códigos
│   │   ├── export_service.py     # Exportación de códigos
│   │   ├── html_renderer.py      # Renderizado de templates HTML
│   │   └── carnet_designer.py    # Diseño de carnets (PIL)
│   │
│   ├── views/                # Capa de presentación (View)
│   │   ├── __init__.py
│   │   ├── main_window.py    # Ventana principal
│   │   ├── login_window.py   # Ventana de login
│   │   ├── carnet_window.py  # Panel de creación de carnets
│   │   └── widgets/          # Widgets reutilizables
│   │       ├── __init__.py
│   │       ├── generation_panel.py      # Panel de generación
│   │       ├── list_panel.py            # Panel de listado
│   │       ├── carnet_preview_panel.py  # Vista previa de carnet
│   │       ├── carnet_controls_panel.py # Controles de diseño de carnet
│   │       └── carnet_employees_panel.py # Lista de empleados para carnet
│   │
│   ├── controllers/          # Controladores (Presenter)
│   │   ├── __init__.py
│   │   ├── main_controller.py  # Controlador principal
│   │   └── carnet_controller.py # Controlador de carnets
│   │
│   └── utils/               # Utilidades
│       ├── __init__.py
│       ├── file_utils.py     # Utilidades de archivos
│       ├── auth_utils.py     # Utilidades de autenticación
│       ├── id_generator.py   # Generador de IDs personalizados
│       ├── html_parser.py    # Parser de templates HTML
│       └── template_generator.py # Generador de templates HTML
│
├── config/                   # Configuración
│   ├── __init__.py
│   └── settings.py           # Configuración centralizada
│
├── .env                      # Variables de entorno (usuarios y contraseñas)
├── .env.example              # Ejemplo de archivo de configuración
├── .gitignore                # Archivos ignorados por Git
├── run.sh                    # Script de ejecución (usa entorno virtual)
│
├── data/                     # Datos de la aplicación
│   ├── codigos_barras.db    # Base de datos SQLite (se crea automáticamente)
│   ├── codigos_generados/   # Directorio con imágenes (se crea automáticamente)
│   ├── backups/             # Backups automáticos de la base de datos
│   ├── carnets/             # Carnets generados (se crea automáticamente)
│   └── templates_carnet/    # Templates HTML para diseño de carnets
│
├── tests/                    # Pruebas unitarias (estructura preparada)
│   └── __init__.py
│
├── env/                      # Entorno virtual
├── requirements.txt          # Dependencias del proyecto
└── README.md                 # Este archivo
```

## Base de Datos

La aplicación utiliza SQLite como base de datos local. El archivo `codigos_barras.db` se crea automáticamente al ejecutar la aplicación por primera vez.

### Estructura de la Tabla

- `id`: Identificador único del registro (auto-incremental)
- `codigo_barras`: ID único aleatorio alfanumérico codificado en el código de barras
- `id_unico`: ID único aleatorio alfanumérico (mismo que codigo_barras)
- `fecha_creacion`: Timestamp de creación
- `nombre_empleado`: Nombre del empleado asociado al código
- `descripcion`: Código de empleado (campo obligatorio)
- `formato`: Formato del código de barras utilizado (Code128, EAN13, EAN8, Code39)
- `nombre_archivo`: Nombre del archivo de imagen generado

## Notas Técnicas

### Arquitectura MVP

El proyecto sigue el patrón **Model-View-Presenter (MVP)**:

- **Model**: `src/models/` - Gestiona el acceso a datos y la persistencia
- **View**: `src/views/` - Componentes de la interfaz de usuario
- **Presenter/Controller**: `src/controllers/` - Coordina la lógica entre modelos y vistas
- **Services**: `src/services/` - Contiene la lógica de negocio reutilizable

### Características Técnicas

- Los códigos de barras se generan como imágenes PNG en el directorio `data/codigos_generados/`
- Cada código tiene un ID único aleatorio alfanumérico de 6 caracteres (0-9, A-Z) que garantiza la unicidad
- El sistema verifica duplicados antes de generar cada ID, asegurando que no se repitan
- El ID generado es el valor que se codifica en el código de barras y aparece como texto debajo del código
- Al escanear el código de barras, se leerá exactamente ese ID único
- La base de datos incluye índices para optimizar las búsquedas
- Los nombres de archivo exportados siguen el formato: `nombre_empleado_codigo_barras.png`
- Configuración centralizada en `config/settings.py` para facilitar el mantenimiento
- Separación clara de responsabilidades que facilita el escalado y mantenimiento
- **Backup automático**: Se crean backups automáticos antes de operaciones críticas (eliminar, limpiar BD)
- **Gestión optimizada de conexiones**: Uso de context managers para mejor manejo de recursos
- **Limpieza automática de backups**: Se mantienen solo los 10 backups más recientes

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

## Seguridad y Autenticación

La aplicación incluye un sistema completo de autenticación con roles de usuario. Al iniciar la aplicación, se mostrará una ventana de login donde debe ingresar sus credenciales.

### Configuración de Usuarios

1. **Archivo `.env`**: Cree un archivo `.env` en la raíz del proyecto (puede copiar `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. **Configurar usuarios**: Edite el archivo `.env` y configure los usuarios administradores y regulares:
   ```env
   # Administradores del sistema
   # Formato: usuario:contraseña
   ADMIN_USERS=admin:admin123,supervisor:super123
   
   # Usuarios del sistema
   # Formato: usuario:contraseña
   REGULAR_USERS=usuario:user123,empleado:emp123
   ```

3. **Importante**: 
   - El archivo `.env` está en `.gitignore` y no se subirá al repositorio
   - Cambie las contraseñas por defecto en producción
   - Use contraseñas seguras para proteger sus datos
   - Puede agregar múltiples usuarios separados por comas en cada variable

### Roles de Usuario

La aplicación soporta dos roles:

- **Administrador (`admin`)**: Tiene acceso completo a todas las funcionalidades, incluyendo:
  - Backup de base de datos
  - Limpiar base de datos
  - Limpiar imágenes huérfanas
  - Todas las funciones de usuario regular

- **Usuario (`user`)**: Tiene acceso a las funcionalidades básicas:
  - Generar códigos de barras
  - Ver y buscar códigos
  - Exportar códigos
  - Crear carnets
  - **NO** tiene acceso a funciones de administración

### Ventana de Login

Al iniciar la aplicación, se mostrará una ventana de login moderna donde debe:
1. Ingresar su nombre de usuario
2. Ingresar su contraseña
3. Hacer clic en "Ingresar" o presionar Enter

Si las credenciales son incorrectas, se mostrará un mensaje de error. La aplicación se cerrará si cierra la ventana de login sin autenticarse.

## Backup Automático

La aplicación incluye un sistema de backup automático para proteger sus datos:

### Características

- **Backup automático antes de operaciones críticas**:
  - Antes de eliminar un código individual
  - Antes de limpiar toda la base de datos
  
- **Ubicación de backups**: Los backups se guardan en `data/backups/`

- **Formato de nombres**: `backup_[razon]_[timestamp].db`
  - Ejemplo: `backup_antes_eliminar_id_5_20251111_182905.db`

- **Limpieza automática**: Se mantienen automáticamente solo los 10 backups más recientes

- **Backup manual**: Puede crear backups manuales usando el botón "Backup BD" en la interfaz

### Restaurar desde Backup

Para restaurar un backup:

1. Localice el archivo de backup en `data/backups/`
2. Detenga la aplicación si está en ejecución
3. Reemplace `data/codigos_barras.db` con el archivo de backup deseado
4. Reinicie la aplicación

## Licencia

Este proyecto es de código abierto y está disponible para uso personal y comercial.

---

**Desarrollado por yoquelvisdev**
