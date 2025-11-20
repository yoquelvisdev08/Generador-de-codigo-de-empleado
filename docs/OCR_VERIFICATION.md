# Verificación OCR de Carnets

Este documento explica cómo usar la verificación OCR para asegurar que los carnets generados contengan la información correcta.

## Instalación

### 1. Instalar EasyOCR

EasyOCR es mucho más simple que Tesseract - **solo necesitas instalar el paquete Python**, no requiere instalación externa.

#### Instalación simple:

```bash
pip install easyocr
```

**¡Eso es todo!** EasyOCR descargará automáticamente los modelos necesarios la primera vez que se use.

#### ⚠️ Problema con Python 3.14

Si estás usando **Python 3.14** y encuentras errores al instalar `scikit-image` (dependencia de EasyOCR), tienes estas opciones:

**Opción 1: Usar Python 3.11 o 3.12** (Recomendado)
- Python 3.11 o 3.12 tienen wheels precompilados disponibles
- Crea un nuevo entorno virtual con una versión anterior de Python

**Opción 2: Instalar Visual Studio Build Tools**
- Descarga desde: https://visualstudio.microsoft.com/downloads/
- Instala "Build Tools for Visual Studio"
- Incluye las herramientas de compilación C++ necesarias
- Luego ejecuta: `pip install easyocr`

**Opción 3: Usar el sistema sin OCR**
- El sistema funcionará normalmente sin OCR
- Solo no tendrás verificación automática de carnets
- Puedes instalar OCR más tarde cuando tengas las herramientas necesarias

### 2. Instalar dependencias adicionales (solo para PDFs)

Si quieres verificar PDFs, también necesitas `pdf2image`:

```bash
pip install pdf2image
```

Si tienes problemas con `pdf2image`, también necesitarás instalar `poppler`:

#### Windows:
- Descargar Poppler desde: https://github.com/oschwartz10612/poppler-windows/releases
- Extraer y agregar a PATH

#### Linux:
```bash
sudo apt-get install poppler-utils
```

#### macOS:
```bash
brew install poppler
```

### 3. Primera ejecución

La primera vez que uses EasyOCR, descargará los modelos de reconocimiento (esto puede tomar unos minutos). Las siguientes veces será mucho más rápido.

## Ventajas de EasyOCR

Según [PyImageSearch](https://pyimagesearch.com/2020/09/14/getting-started-with-easyocr-for-optical-character-recognition/), EasyOCR tiene varias ventajas:

1. **Instalación simple**: Solo `pip install easyocr`
2. **No requiere instalación externa**: A diferencia de Tesseract, no necesitas instalar software adicional
3. **Soporte para 58 idiomas**: Incluyendo español e inglés
4. **API simple**: Solo dos líneas de código para hacer OCR
5. **Soporte GPU opcional**: Puede usar GPU CUDA para acelerar (configurable)

## Uso

### Verificación Individual

```python
from src.services.ocr_verifier import OCRVerifier
from pathlib import Path

# Inicializar verificador (descargará modelos la primera vez)
verificador = OCRVerifier()

# Datos esperados del carnet
datos_esperados = {
    'nombres': 'Juan',
    'apellidos': 'Pérez',
    'descripcion': 'EMP001',
    'id_unico': 'ABC123XYZ'
}

# Verificar carnet PNG
ruta_carnet = Path('carnet_juan_perez.png')
exito, mensaje, detalles = verificador.verificar_carnet(
    ruta_carnet,
    datos_esperados,
    umbral_similitud=0.8  # 80% de similitud requerida
)

if exito:
    print("✓ Carnet verificado correctamente")
else:
    print(f"✗ Error: {mensaje}")
    print(f"Detalles: {detalles}")
```

### Verificación Masiva

```python
# Lista de archivos y datos
rutas_archivos = [
    Path('carnet_1.png'),
    Path('carnet_2.png'),
    Path('carnet_3.pdf')
]

datos_empleados = [
    {'nombres': 'Juan', 'apellidos': 'Pérez', 'descripcion': 'EMP001', 'id_unico': 'ABC123'},
    {'nombres': 'María', 'apellidos': 'García', 'descripcion': 'EMP002', 'id_unico': 'DEF456'},
    {'nombres': 'Carlos', 'apellidos': 'López', 'descripcion': 'EMP003', 'id_unico': 'GHI789'}
]

# Verificar todos
resultados = verificador.verificar_carnets_masivos(
    rutas_archivos,
    datos_empleados
)

# Revisar resultados
for ruta, (exito, mensaje, detalles) in resultados.items():
    if exito:
        print(f"✓ {ruta.name}: OK")
    else:
        print(f"✗ {ruta.name}: {mensaje}")
```

## Integración en Generación de Carnets

El servicio OCR se integra automáticamente en el proceso de generación de carnets para verificar automáticamente cada carnet generado.

### Funcionamiento Automático

1. **Generación**: Se genera el carnet (PNG o PDF)
2. **Verificación**: EasyOCR extrae el texto del carnet
3. **Comparación**: Se compara con los datos esperados (nombres, apellidos, código, ID único)
4. **Regeneración**: Si falla, se regenera automáticamente (hasta 2 intentos)
5. **Resultado**: Se guarda el carnet verificado o el último intento

## Parámetros de Verificación

### umbral_similitud

Controla qué tan estricta es la verificación:
- `0.8` (80%): Recomendado para la mayoría de casos
- `0.9` (90%): Más estricto, puede fallar con fuentes decorativas
- `0.7` (70%): Más permisivo, útil para imágenes de baja calidad

### Configuración de GPU

Por defecto, EasyOCR usa CPU. Si tienes una GPU CUDA, puedes acelerar el proceso editando `src/services/ocr_verifier.py`:

```python
# Cambiar gpu=False a gpu=True
self.reader = easyocr.Reader(['es', 'en'], gpu=True)
```

**Nota**: Requiere PyTorch con soporte CUDA instalado.

## Solución de Problemas

### Error: "EasyOCR no se pudo inicializar"
- Asegúrate de tener EasyOCR instalado: `pip install easyocr`
- La primera vez puede tardar mientras descarga los modelos
- Verifica tu conexión a internet (necesaria para descargar modelos)

### Error: "No se pudo extraer texto"
- Verifica que el archivo exista y sea accesible
- Para PDFs, asegúrate de tener `poppler` instalado
- Verifica que el archivo no esté corrupto

### Baja precisión en la verificación
- Aumenta el DPI de las imágenes generadas (actualmente 600 DPI)
- Ajusta el `umbral_similitud` según tus necesidades
- Verifica que las fuentes en el template HTML sean claras y legibles

### Lento en la primera ejecución
- Es normal, EasyOCR descarga los modelos la primera vez
- Los modelos se guardan en cache, las siguientes veces será más rápido
- Considera usar GPU si tienes una disponible

## Notas

- La verificación OCR es opcional y no bloquea la generación de carnets
- El proceso de OCR puede ser lento para muchos archivos (considera procesar en paralelo)
- La precisión depende de la calidad de la imagen y la fuente usada
- Para mejor precisión, usa fuentes claras y de buen tamaño en los templates HTML
- EasyOCR funciona mejor con texto impreso que con texto manuscrito

## Referencias

- [EasyOCR en PyImageSearch](https://pyimagesearch.com/2020/09/14/getting-started-with-easyocr-for-optical-character-recognition/)
- [Documentación oficial de EasyOCR](https://github.com/JaidedAI/EasyOCR)
