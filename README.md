# Generador de Códigos de Barras

Aplicación de escritorio con interfaz gráfica para generar códigos de barras con ID único y gestión mediante base de datos local SQLite.

**by yoquelvisdev**

## Características

- **Sistema de autenticación**: Login con usuario y contraseña, soporte para roles (admin/user)
- **Generación de códigos de barras**: Múltiples formatos (Code128, EAN13, EAN8, Code39)
- **ID personalizado**: Configuración de tipo de caracteres, longitud, inclusión de nombre y texto personalizado
- **Base de datos local SQLite**: Almacenamiento persistente con backups automáticos
- **Verificación de duplicados**: Antes de generar nuevos códigos
- **Interfaz gráfica moderna**: Diseño profesional con PyQt6 y navbar de navegación
- **Vista previa en tiempo real**: Actualización automática del ID mientras configura opciones
- **Búsqueda y filtrado**: Búsqueda avanzada de códigos existentes
- **Exportación**: Exportación individual o masiva de imágenes
- **Importación/Exportación Excel**: Gestión masiva de datos mediante archivos Excel
- **Editor de Carnets**: Diseño de carnets de identificación con templates HTML
- **Verificación OCR automática**: Verificación automática de carnets generados usando Tesseract OCR para asegurar que los datos se renderizaron correctamente
- **Gestión de Usuarios**: Panel administrativo para crear usuarios, cambiar contraseñas y eliminar usuarios
- **Gestión completa**: Crear, ver, eliminar códigos y gestionar imágenes
- **Control de permisos**: Los administradores tienen acceso a funciones adicionales
- **Separación de nombres y apellidos**: Manejo independiente de nombres y apellidos para mejor organización de datos

## Requisitos del Sistema

- Python 3.8 o superior
- Windows, Linux o macOS

### Requisitos Adicionales para macOS

Si está usando macOS, necesitará instalar la librería `zbar` (requerida por `pyzbar` para la lectura de códigos de barras):

```bash
brew install zbar
```

**Nota:** El script de activación del entorno virtual está configurado para configurar automáticamente las variables de entorno necesarias en macOS. Si tiene problemas, asegúrese de que Homebrew esté instalado y que `zbar` esté correctamente instalado.

### Requisitos Adicionales para Verificación OCR (Opcional)

La aplicación incluye verificación OCR automática de carnets generados usando **Tesseract OCR**. Esta funcionalidad es opcional pero recomendada para asegurar la calidad de los carnets generados.

**Para habilitar la verificación OCR:**

1. **Instalar Tesseract OCR** (aplicación separada):
   - **Windows**: Descarga el instalador desde https://github.com/UB-Mannheim/tesseract/wiki
   - Durante la instalación, marca la opción "Add to PATH" o instala en la ruta predeterminada: `C:\Program Files\Tesseract-OCR\`
   - Selecciona los idiomas "Spanish" y "English" durante la instalación
   
2. **Instalar el paquete Python** (ya incluido en requirements.txt):
   ```bash
   pip install pytesseract
   ```

3. **Verificar la instalación**:
   ```bash
   tesseract --version
   ```

**Nota**: Si Tesseract no está en PATH, la aplicación intentará encontrarlo automáticamente en las rutas comunes de Windows. Si está en otra ubicación, puedes configurarlo manualmente en el código si es necesario.

**Sin Tesseract**: La aplicación funcionará normalmente, pero la verificación OCR estará deshabilitada y los carnets se generarán sin verificación automática.

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
- PyQt6-WebEngine: Para renderizado de HTML en carnets
- python-barcode: Para generar códigos de barras
- Pillow: Para el procesamiento de imágenes
- pyzbar: Para la lectura y validación de códigos de barras (requiere zbar en macOS)
- numpy: Para el procesamiento de imágenes
- python-dotenv: Para gestionar variables de entorno y configuración de seguridad
- openpyxl: Para importación y exportación de datos en formato Excel
- pdf2image: Para conversión de PDF a imágenes
- pytesseract: Para verificación OCR de carnets generados (opcional, requiere Tesseract OCR instalado)

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
1. Si es la primera vez (no hay usuarios registrados), se mostrará una ventana de registro para crear el primer usuario administrador
2. Si ya hay usuarios registrados, se mostrará una ventana de login
3. Ingrese su usuario y contraseña
4. Después del login exitoso, se abrirá la ventana principal de la aplicación

**En macOS:** Si obtiene un error relacionado con `zbar`, asegúrese de haber instalado `zbar` con Homebrew (ver requisitos adicionales arriba) y de que el entorno virtual esté activado correctamente. El script de activación configura automáticamente las variables de entorno necesarias.

### Navegación

La aplicación cuenta con un navbar permanente en la parte superior con los siguientes menús:

**Menú Tools:**
- **Código de Barras**: Acceso al generador de códigos de barras
- **Crear Carnet**: Acceso al editor de carnets de identificación

**Menú Usuario (solo para administradores):**
- **Gestión de Usuarios**: Panel administrativo para gestionar usuarios del sistema

### Generar un código de barras

1. Acceda a "Código de Barras" desde el menú **Tools** en el navbar
2. Ingrese los nombres del empleado en el campo "Nombres del Empleado"
3. Ingrese los apellidos del empleado en el campo "Apellidos del Empleado"
4. Ingrese el código de empleado en el campo "Código de Empleado" (campo obligatorio)
5. Seleccione el formato deseado (Code128, EAN13, EAN8, Code39)
6. Configure las opciones de generación de ID:
   - Tipo de caracteres: Alfanumérico, Numérico, o Solo Letras
   - Cantidad de caracteres (por defecto: 10)
   - Opcionalmente, incluya el nombre del empleado en el código
   - Opcionalmente, cree un texto personalizado para el código de barras (aparece un campo de entrada cuando se marca esta opción)
7. El ID se generará automáticamente y se mostrará en tiempo real en la vista previa
8. Haga clic en "Generar Código de Barras"

El sistema generará automáticamente un ID único personalizado según las opciones seleccionadas. El ID aparecerá debajo del código y es el valor que se leerá al escanearlo.

### Formatos de Código de Barras

- **Code128**: Acepta caracteres alfanuméricos (hasta 80 caracteres)
- **EAN13**: Requiere exactamente 13 dígitos numéricos
- **EAN8**: Requiere exactamente 8 dígitos numéricos
- **Code39**: Acepta caracteres alfanuméricos y algunos especiales (hasta 43 caracteres)

### Funcionalidades Adicionales

#### Gestión de Códigos de Barras

- **Búsqueda**: Use el campo de búsqueda para filtrar códigos por código de barras, ID único, nombres, apellidos o código de empleado
- **Vista Previa**: Al seleccionar un código en la tabla, la imagen se muestra automáticamente en el panel de generación
- **Exportar Seleccionados**: Seleccione múltiples códigos (Ctrl+clic o Shift+clic) y exporte las imágenes a una carpeta. Los archivos se nombran como: `nombre_empleado_codigo_barras.png`
- **Exportar Todos (ZIP)**: Exporta todos los códigos en un archivo ZIP con el mismo formato de nombres
- **Eliminar**: Seleccione un código y haga clic en "Eliminar" para removerlo de la base de datos

#### Funcionalidades Excel

- **Exportar Data en Excel**: Exporta todos los datos de la base de datos a un archivo Excel con formato profesional. Las columnas exportadas son: ID, Código de Barras, ID Único, Fecha de Creación, Nombres, Apellidos, Código de Empleado y Formato
- **Importar Data en Excel**: Importa datos desde un archivo Excel y genera códigos de barras automáticamente. El proceso incluye:
  - Validación de datos (columnas requeridas: "Nombres", "Apellidos" y "Código de Empleado")
  - Generación automática de códigos de barras
  - Validación de códigos generados
  - Detección de duplicados
  - Opción de regenerar códigos que fallan la validación
  - Diálogo de progreso para mantener al usuario informado
  - **Normalización de formatos**: Si el Excel contiene formatos distintos de Code128 (EAN13, EAN8, Code39), estos se convierten automáticamente a Code128 durante la importación. Si no se especifica formato en el Excel, se utiliza el formato seleccionado en el dropdown de la interfaz o Code128 por defecto
- **Descargar Excel de Ejemplo**: Descarga un archivo Excel de ejemplo con el formato correcto para importar datos. El archivo incluye las columnas: Nombres, Apellidos, Código de Empleado y Formato (opcional). La columna "Formato (opcional)" permite especificar un formato, pero todos los formatos se normalizarán a Code128 durante la importación

#### Funcionalidades de Administración (Solo Admin)

- **Backup BD**: Crea un backup de la base de datos con timestamp
- **Limpiar Base de Datos**: Elimina todos los códigos de la base de datos (acción irreversible)
- **Limpiar Imágenes Huérfanas**: Elimina imágenes que no tienen registro en la base de datos

#### Gestión de Usuarios (Solo Admin)

Los administradores pueden acceder a un panel completo de gestión de usuarios desde el menú **Usuario** > **Gestión de Usuarios** en el navbar.

**Funcionalidades disponibles:**

1. **Crear Nuevo Usuario**:
   - Ingrese nombre completo, email, usuario y contraseña
   - Seleccione el rol (admin o user)
   - Validación automática de email, usuarios y contraseñas
   - Verificación de duplicados
   - Las contraseñas deben tener mínimo 6 caracteres
   - Los usuarios deben tener mínimo 3 caracteres

2. **Cambiar Contraseña**:
   - Seleccione un usuario del dropdown
   - Ingrese y confirme la nueva contraseña
   - La contraseña se actualiza con hash seguro SHA-256 y salt

3. **Ver Usuarios Registrados**:
   - Tabla con todos los usuarios del sistema
   - Información mostrada: Usuario, Nombre, Email, Rol, Fecha de Creación
   - Diseño oscuro para mejor visibilidad

4. **Eliminar Usuario**:
   - Seleccione un usuario de la tabla
   - Haga clic en "Eliminar Usuario"
   - **Protección**: No puede eliminar su propio usuario
   - Confirmación requerida antes de eliminar

**Seguridad:**
- Todas las contraseñas se almacenan con hash SHA-256 y salt único
- Validación de formato de email
- Verificación de usuarios y emails únicos
- Todas las acciones se registran en los logs del sistema

#### Editor de Carnets

- **Crear Carnet**: Acceda desde el menú **Tools** > **Crear Carnet** para diseñar carnets de identificación con templates HTML personalizables
  - **Templates HTML personalizables**: Seleccione un template HTML desde el directorio `data/templates_carnet/` o cree uno nuevo
  - **Variables dinámicas**: El sistema detecta automáticamente las variables del template (como `{{nombre}}`, `{{codigo_barras}}`, `{{nombres}}`, `{{apellidos}}`, `{{descripcion}}`, `{{id_unico}}`, etc.) y genera campos de entrada para cada una
  - **Vista previa en tiempo real**: Visualice cómo se verá el carnet antes de generarlo
  - **Generación individual**: Genere un carnet para el empleado seleccionado en la lista
  - **Generación masiva**: Genere carnets para todos los empleados de la base de datos con un solo clic, con diálogo de progreso que muestra el estado de la generación
  - **Interfaz unificada**: Los controles de template HTML y variables están consolidados en un solo panel para mejor organización
  - **Verificación OCR automática**: Si Tesseract OCR está instalado, el sistema verifica automáticamente que los datos del carnet generado sean correctos comparando el texto extraído con OCR contra los datos esperados. Si la verificación falla, el sistema reintenta la generación automáticamente hasta 2 veces para asegurar la calidad

### Verificación OCR de Carnets

La aplicación incluye un sistema de verificación OCR automática que asegura que los carnets generados contengan los datos correctos.

**Cómo funciona:**

1. **Generación del carnet**: Se genera el carnet con los datos del empleado desde la base de datos
2. **Extracción de texto**: Tesseract OCR extrae todo el texto visible del carnet generado
3. **Comparación**: Se compara el texto extraído con los datos esperados (nombres, apellidos, descripción, ID único)
4. **Reintentos automáticos**: Si algún campo no se encuentra, el sistema reintenta la generación automáticamente (hasta 2 veces)
5. **Resultado**: El carnet se marca como verificado si todos los campos se encuentran correctamente

**Campos verificados:**
- Nombres del empleado
- Apellidos del empleado
- Código de empleado (descripción)
- ID único del código de barras

**Ventajas:**
- Asegura la calidad de los carnets generados
- Detecta problemas de renderizado automáticamente
- Reintenta la generación si hay errores
- Funciona tanto para generación individual como masiva

**Nota**: La verificación OCR es opcional. Si Tesseract no está instalado, los carnets se generarán normalmente pero sin verificación automática.

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
│   │   ├── excel_service.py      # Importación y exportación Excel
│   │   ├── html_renderer.py      # Renderizado de templates HTML
│   │   ├── carnet_designer.py    # Diseño de carnets (PIL)
│   │   └── ocr_verifier.py       # Verificación OCR de carnets (Tesseract)
│   │
│   ├── views/                # Capa de presentación (View)
│   │   ├── __init__.py
│   │   ├── main_window.py    # Ventana principal
│   │   ├── login_window.py   # Ventana de login
│   │   ├── register_window.py # Ventana de registro de usuarios
│   │   ├── carnet_window.py  # Panel de creación de carnets
│   │   ├── user_management_panel.py # Panel de gestión de usuarios
│   │   └── widgets/          # Widgets reutilizables
│   │       ├── __init__.py
│   │       ├── generation_panel.py      # Panel de generación
│   │       ├── list_panel.py            # Panel de listado
│   │       ├── progress_dialog.py       # Diálogo de progreso para operaciones largas
│   │       ├── carnet_preview_panel.py  # Vista previa de carnet
│   │       ├── carnet_controls_panel.py  # Controles de diseño de carnet
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
│       ├── password_utils.py # Utilidades para hash de contraseñas
│       ├── user_logger.py    # Sistema de logging de acciones de usuarios
│       ├── id_generator.py   # Generador de IDs personalizados
│       ├── html_parser.py    # Parser de templates HTML
│       └── template_generator.py # Generador de templates HTML
│
├── config/                   # Configuración
│   ├── __init__.py
│   └── settings.py           # Configuración centralizada
│
├── .env                      # Variables de entorno (opcional, ya no se usa para autenticación)
├── .env.example              # Ejemplo de archivo de configuración (legacy)
├── .gitignore                # Archivos ignorados por Git
├── run.sh                    # Script de ejecución (usa entorno virtual)
│
├── data/                     # Datos de la aplicación
│   ├── codigos_barras.db    # Base de datos SQLite (se crea automáticamente)
│   ├── codigos_generados/   # Directorio con imágenes (se crea automáticamente)
│   ├── backups/             # Backups automáticos de la base de datos
│   ├── carnets/             # Carnets generados (se crea automáticamente)
│   ├── templates_carnet/    # Templates HTML para diseño de carnets
│   └── logs/                 # Logs de acciones de usuarios (se crea automáticamente)
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

### Tabla `codigos_barras`

La tabla `codigos_barras` contiene los siguientes campos:

- `id`: Identificador único del registro (auto-incremental)
- `codigo_barras`: ID único aleatorio alfanumérico codificado en el código de barras
- `id_unico`: ID único aleatorio alfanumérico (mismo que codigo_barras)
- `fecha_creacion`: Timestamp de creación
- `nombre_empleado`: Nombre del empleado asociado al código (legacy, se mantiene para compatibilidad)
- `nombres`: Nombres del empleado (campo nuevo, separado de apellidos)
- `apellidos`: Apellidos del empleado (campo nuevo, separado de nombres)
- `descripcion`: Código de empleado (campo obligatorio)
- `formato`: Formato del código de barras utilizado (Code128, EAN13, EAN8, Code39)
- `nombre_archivo`: Nombre del archivo de imagen generado (usado principalmente para carnets)

**Nota**: El sistema mantiene compatibilidad con datos antiguos que usan `nombre_empleado`. Los nuevos registros usan `nombres` y `apellidos` por separado.

**Nota**: El campo `nombre_archivo` no se muestra en la vista de códigos de barras, ya que es exclusivo del generador de carnets. En la vista de códigos de barras, el nombre del archivo se genera dinámicamente cuando es necesario.

### Tabla `usuarios`

La tabla `usuarios` contiene los siguientes campos:

- `id`: Identificador único del registro (auto-incremental)
- `nombre`: Nombre completo del usuario
- `email`: Email del usuario (único)
- `usuario`: Nombre de usuario para login (único)
- `contraseña`: Hash de la contraseña con formato "hash:salt"
- `rol`: Rol del usuario ('admin' o 'user')
- `fecha_creacion`: Timestamp de creación del usuario

**Seguridad**: Las contraseñas se almacenan con hash SHA-256 y salt único, nunca en texto plano.

**Gestión de usuarios**: El sistema incluye métodos para:
- Crear nuevos usuarios con validación de duplicados
- Actualizar contraseñas de usuarios existentes
- Eliminar usuarios del sistema
- Obtener información de usuarios
- Autenticar credenciales de login

## Notas Técnicas

### Arquitectura MVP

El proyecto sigue el patrón **Model-View-Presenter (MVP)**:

- **Model**: `src/models/` - Gestiona el acceso a datos y la persistencia
- **View**: `src/views/` - Componentes de la interfaz de usuario
- **Presenter/Controller**: `src/controllers/` - Coordina la lógica entre modelos y vistas
- **Services**: `src/services/` - Contiene la lógica de negocio reutilizable

### Características Técnicas

- Los códigos de barras se generan como imágenes PNG en el directorio `data/codigos_generados/`
- Cada código tiene un ID único aleatorio alfanumérico configurable que garantiza la unicidad
- El sistema verifica duplicados antes de generar cada ID, asegurando que no se repitan
- El ID generado puede incluir:
  - Texto personalizado (si se especifica)
  - Nombre del empleado (opcional)
  - Caracteres aleatorios según la configuración (alfanumérico, numérico, solo letras)
- El ID es el valor que se codifica en el código de barras y aparece como texto debajo del código
- Al escanear el código de barras, se leerá exactamente ese ID único
- La base de datos incluye índices para optimizar las búsquedas
- Los nombres de archivo exportados siguen el formato: `nombre_empleado_codigo_barras.png`
- Configuración centralizada en `config/settings.py` para facilitar el mantenimiento
- Separación clara de responsabilidades que facilita el escalado y mantenimiento
- **Backup automático**: Se crean backups automáticos antes de operaciones críticas (eliminar, limpiar BD)
- **Gestión optimizada de conexiones**: Uso de context managers para mejor manejo de recursos
- **Limpieza automática de backups**: Se mantienen solo los 10 backups más recientes
- **Importación/Exportación Excel**: Sistema completo para gestión masiva de datos con validación y generación automática
- **Interfaz con scroll**: El panel de generación incluye scroll vertical para mejor navegación
- **Navbar de navegación**: Barra de navegación permanente con menús desplegables (Tools y Usuario) para acceso rápido a funcionalidades principales
- **Autenticación basada en BD**: Sistema de autenticación seguro con usuarios almacenados en base de datos y contraseñas hasheadas
- **Gestión de usuarios integrada**: Panel administrativo completo para crear, editar y eliminar usuarios del sistema
- **Sistema de logging**: Registro automático de todas las acciones de usuarios en archivos de log diarios ubicados en `data/logs/`
- **Información del usuario**: El nombre completo del usuario autenticado se muestra en el navbar
- **Verificación OCR con Tesseract**: Sistema automático de verificación de carnets generados usando Tesseract OCR. Compara el texto extraído del carnet con los datos esperados y reintenta la generación si hay discrepancias
- **Separación de nombres y apellidos**: El sistema ahora maneja nombres y apellidos por separado para mejor organización de datos

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

### Error "Tesseract OCR no está instalado o no está en PATH"

Este error ocurre cuando se intenta usar la verificación OCR pero Tesseract no está instalado o no es accesible. Solución:

1. **Windows**: 
   - Descarga e instala Tesseract OCR desde https://github.com/UB-Mannheim/tesseract/wiki
   - Durante la instalación, marca "Add to PATH" o instala en `C:\Program Files\Tesseract-OCR\`
   - Selecciona los idiomas "Spanish" y "English"
   - Reinicia la aplicación

2. **Verificar instalación**:
   ```bash
   tesseract --version
   ```

3. Si Tesseract está instalado pero no en PATH, la aplicación intentará encontrarlo automáticamente en las rutas comunes de Windows.

**Nota**: La verificación OCR es opcional. La aplicación funcionará sin Tesseract, pero los carnets se generarán sin verificación automática.

## Seguridad y Autenticación

La aplicación incluye un sistema completo de autenticación con roles de usuario basado en base de datos. Los usuarios y contraseñas se almacenan de forma segura en la base de datos SQLite con hash SHA-256 y salt.

### Registro del Primer Usuario

**Primera vez que ejecuta la aplicación:**
1. Si no hay usuarios en la base de datos, se mostrará automáticamente una ventana de registro
2. Complete el formulario con:
   - **Nombre completo**: Su nombre completo
   - **Email**: Su dirección de email (debe ser único)
   - **Usuario**: Nombre de usuario para iniciar sesión (debe ser único, mínimo 3 caracteres)
   - **Contraseña**: Contraseña segura (mínimo 6 caracteres)
   - **Confirmar contraseña**: Repita la contraseña
3. El primer usuario siempre se registra como **administrador**
4. Después del registro exitoso, se abrirá la ventana principal de la aplicación

### Inicio de Sesión

**En ejecuciones posteriores:**
1. Se mostrará una ventana de login
2. Ingrese su nombre de usuario y contraseña
3. Haga clic en "Ingresar" o presione Enter
4. Si las credenciales son correctas, se abrirá la ventana principal

### Seguridad

- **Contraseñas hasheadas**: Todas las contraseñas se almacenan con hash SHA-256 y salt único
- **Almacenamiento en BD**: Los usuarios se almacenan en la tabla `usuarios` de la base de datos SQLite
- **Validación de email**: El sistema valida el formato de email antes de registrar
- **Usuarios únicos**: No se permiten usuarios o emails duplicados
- **Nota**: El archivo `.env` ya no se utiliza para autenticación. Puede eliminarlo si no lo necesita para otras configuraciones.

### Roles de Usuario

La aplicación soporta dos roles:

- **Administrador (`admin`)**: Tiene acceso completo a todas las funcionalidades, incluyendo:
  - Gestión de usuarios (crear, editar, eliminar usuarios)
  - Cambiar contraseñas de cualquier usuario
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
  - **NO** tiene acceso al menú "Usuario" ni gestión de usuarios

### Información del Usuario

- El nombre completo del usuario autenticado se muestra en el navbar de la aplicación (parte superior derecha)
- Esto permite identificar fácilmente quién está usando el sistema en cada momento

## Sistema de Logging de Usuarios

La aplicación registra automáticamente todas las acciones importantes de los usuarios en archivos de log.

### Características

- **Logs diarios**: Se crea un archivo de log por día con formato `user_actions_YYYYMMDD.log`
- **Ubicación**: Los logs se guardan en `data/logs/`
- **Formato**: Cada línea contiene timestamp, usuario, acción y detalles
  ```
  2025-11-15 09:20:01 | Usuario: admin | Acción: Inicio de sesión
  2025-11-15 09:25:30 | Usuario: admin | Acción: Generar código de barras | Detalles: Empleado: Juan Pérez, Código: EMP001, Formato: Code128
  ```

### Acciones Registradas

El sistema registra las siguientes acciones:
- Inicio de sesión
- Registro de nuevos usuarios
- Gestión de usuarios (crear usuario, cambiar contraseña, eliminar usuario)
- Generación de códigos de barras
- Eliminación de códigos
- Exportación de códigos (individual, masiva, Excel)
- Importación desde Excel
- Creación de backups
- Limpieza de base de datos
- Limpieza de imágenes huérfanas
- Búsquedas realizadas
- Generación de carnets
- Verificación OCR de carnets (si Tesseract está disponible)

### Uso de los Logs

Los logs permiten:
- Auditoría de acciones realizadas por cada usuario
- Seguimiento de cambios en el sistema
- Identificación de problemas o errores
- Análisis de uso del sistema

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
