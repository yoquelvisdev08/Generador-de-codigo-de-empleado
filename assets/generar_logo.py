"""
Script para generar el logo de la aplicación
"""
from PIL import Image, ImageDraw, ImageFont
import os

def crear_logo():
    """Crea el logo principal de la aplicación"""
    # Tamaño del logo
    width, height = 400, 400
    
    # Crear imagen con fondo transparente
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Color principal: azul moderno
    color_principal = (102, 126, 234, 255)  # #667eea
    color_secundario = (118, 75, 162, 255)  # #764ba2
    color_oscuro = (26, 26, 46, 255)  # #1a1a2e
    
    # Dibujar círculo de fondo con gradiente (simulado con círculos concéntricos)
    center_x, center_y = width // 2, height // 2
    max_radius = 180
    
    for i in range(max_radius, 0, -5):
        # Interpolación de color del gradiente
        t = i / max_radius
        r = int(color_principal[0] * t + color_secundario[0] * (1 - t))
        g = int(color_principal[1] * t + color_secundario[1] * (1 - t))
        b = int(color_principal[2] * t + color_secundario[2] * (1 - t))
        
        draw.ellipse(
            [center_x - i, center_y - i, center_x + i, center_y + i],
            fill=(r, g, b, 255)
        )
    
    # Dibujar barras de código de barras estilizadas (representación visual)
    bar_width = 8
    bar_height = 120
    bar_spacing = 12
    num_bars = 7
    
    start_x = center_x - (num_bars * (bar_width + bar_spacing)) // 2
    start_y = center_y - bar_height // 2
    
    # Alturas variables para efecto visual
    heights = [100, 120, 90, 120, 100, 110, 95]
    
    for i in range(num_bars):
        x = start_x + i * (bar_width + bar_spacing)
        current_height = heights[i]
        y = start_y + (bar_height - current_height) // 2
        
        # Barras blancas con sombra
        draw.rectangle(
            [x, y, x + bar_width, y + current_height],
            fill=(255, 255, 255, 255)
        )
    
    # Guardar logo principal
    img.save('logo.png', 'PNG')
    print("Logo principal creado: logo.png")
    
    # Crear versión pequeña para ícono
    icon_sizes = [16, 32, 48, 64, 128, 256]
    for size in icon_sizes:
        icon = img.resize((size, size), Image.Resampling.LANCZOS)
        icon.save(f'logo_{size}x{size}.png', 'PNG')
        print(f"Ícono {size}x{size} creado")

def crear_logo_horizontal():
    """Crea una versión horizontal del logo con texto"""
    width, height = 800, 200
    
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colores
    color_principal = (102, 126, 234, 255)
    color_secundario = (118, 75, 162, 255)
    
    # Dibujar el ícono pequeño a la izquierda
    icon_size = 150
    center_x, center_y = icon_size // 2 + 25, height // 2
    
    # Círculo con gradiente
    max_radius = 70
    for i in range(max_radius, 0, -2):
        t = i / max_radius
        r = int(color_principal[0] * t + color_secundario[0] * (1 - t))
        g = int(color_principal[1] * t + color_secundario[1] * (1 - t))
        b = int(color_principal[2] * t + color_secundario[2] * (1 - t))
        
        draw.ellipse(
            [center_x - i, center_y - i, center_x + i, center_y + i],
            fill=(r, g, b, 255)
        )
    
    # Barras pequeñas
    bar_width = 4
    bar_height = 50
    bar_spacing = 6
    num_bars = 7
    
    start_x = center_x - (num_bars * (bar_width + bar_spacing)) // 2
    start_y = center_y - bar_height // 2
    
    heights = [40, 50, 35, 50, 40, 45, 38]
    
    for i in range(num_bars):
        x = start_x + i * (bar_width + bar_spacing)
        current_height = heights[i]
        y = start_y + (bar_height - current_height) // 2
        
        draw.rectangle(
            [x, y, x + bar_width, y + current_height],
            fill=(255, 255, 255, 255)
        )
    
    # Texto (usando fuente por defecto si no hay fuente personalizada)
    try:
        # Intentar usar una fuente del sistema
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        font_subtitle = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except:
        try:
            font_title = ImageFont.truetype("arial.ttf", 60)
            font_subtitle = ImageFont.truetype("arial.ttf", 24)
        except:
            # Usar fuente por defecto
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()
    
    # Texto principal
    text_x = icon_size + 50
    draw.text((text_x, 50), "Generador de Códigos", fill=color_principal, font=font_title)
    draw.text((text_x, 120), "by yoquelvisdev", fill=(100, 100, 100, 255), font=font_subtitle)
    
    img.save('logo_horizontal.png', 'PNG')
    print("Logo horizontal creado: logo_horizontal.png")

if __name__ == "__main__":
    # Cambiar al directorio de assets
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("Generando logos...")
    crear_logo()
    crear_logo_horizontal()
    print("\n¡Logos generados exitosamente!")

