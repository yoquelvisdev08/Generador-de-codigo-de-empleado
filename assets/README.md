# Assets - Logos de la Aplicación

Este directorio contiene los logos e íconos de la aplicación "Generador de Códigos de Barras".

## Archivos Generados

### Logo Principal
- **logo.png** (400x400px): Logo principal con diseño circular y barras de código estilizadas

### Logos Horizontales
- **logo_horizontal.png** (800x200px): Logo con texto "Generador de Códigos by yoquelvisdev"

### Íconos de Aplicación
Diferentes tamaños para uso como ícono de ventana:
- logo_16x16.png
- logo_32x32.png
- logo_48x48.png
- **logo_64x64.png** (usado como ícono de ventana principal)
- logo_128x128.png
- logo_256x256.png

## Diseño del Logo

El logo presenta:
- **Gradiente circular**: De azul (#667eea) a púrpura (#764ba2)
- **Barras estilizadas**: Representación visual de un código de barras
- **Colores corporativos**: Coinciden con el esquema de colores de la aplicación

## Regenerar Logos

Si necesita modificar o regenerar los logos, ejecute:

```bash
cd assets
python3 generar_logo.py
```

El script `generar_logo.py` creará todas las versiones del logo automáticamente.

## Uso en la Aplicación

Los logos se utilizan en:
- **Ventana de Login**: Logo principal (120x120px)
- **Ventana de Registro**: Logo principal (120x120px)
- **Ventana Principal**: Ícono de ventana (64x64px)
- **Íconos del Sistema**: Versiones de 16x16 a 256x256px

## Personalización

Para personalizar los logos:
1. Edite el archivo `generar_logo.py`
2. Modifique los colores en las variables:
   - `color_principal` (azul)
   - `color_secundario` (púrpura)
   - `color_oscuro`
3. Ajuste el tamaño, número de barras o efectos visuales
4. Ejecute el script para generar las nuevas versiones

---

**by yoquelvisdev**

