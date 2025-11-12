"""
Servicio para diseñar y renderizar carnets
"""
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import logging

from src.models.carnet_template import CarnetTemplate
from config.settings import IMAGES_DIR

logger = logging.getLogger(__name__)


class CarnetDesigner:
    """Servicio para diseñar y renderizar carnets"""
    
    def __init__(self):
        """Inicializa el diseñador de carnets"""
        self.template_actual: Optional[CarnetTemplate] = None
    
    def establecer_template(self, template: CarnetTemplate):
        """Establece la plantilla actual"""
        self.template_actual = template
    
    def renderizar_carnet(
        self,
        template: CarnetTemplate,
        nombre_empleado: str,
        codigo_barras_path: Optional[str] = None,
        foto_path: Optional[str] = None,
        cedula: Optional[str] = None,
        cargo: Optional[str] = None,
        empresa: Optional[str] = None,
        web: Optional[str] = None
    ) -> Image.Image:
        """
        Renderiza un carnet con los datos proporcionados
        
        Args:
            template: Plantilla de diseño
            nombre_empleado: Nombre del empleado
            codigo_barras_path: Ruta a la imagen del código de barras
            foto_path: Ruta a la foto del empleado
            cedula: Número de cédula
            cargo: Cargo del empleado
            empresa: Nombre de la empresa
            web: URL del sitio web
            
        Returns:
            Imagen PIL del carnet renderizado
        """
        # Crear imagen base
        imagen = Image.new('RGB', (template.ancho, template.alto), template.fondo_color)
        draw = ImageDraw.Draw(imagen)
        
        # Aplicar fondo con imagen si existe
        if template.fondo_imagen_path and Path(template.fondo_imagen_path).exists():
            try:
                fondo_img = Image.open(template.fondo_imagen_path)
                fondo_img = fondo_img.resize((template.ancho, template.alto))
                
                # Aplicar opacidad
                if template.fondo_opacidad < 1.0:
                    fondo_img = fondo_img.convert('RGBA')
                    alpha = int(255 * template.fondo_opacidad)
                    fondo_img.putalpha(alpha)
                    imagen = imagen.convert('RGBA')
                    imagen = Image.alpha_composite(imagen, fondo_img)
                    imagen = imagen.convert('RGB')
                else:
                    imagen.paste(fondo_img, (0, 0))
            except Exception as e:
                logger.warning(f"Error al cargar imagen de fondo: {e}")
        
        # Cargar logo si existe
        if template.logo_path and Path(template.logo_path).exists():
            try:
                logo = Image.open(template.logo_path)
                logo = logo.resize((template.logo_ancho, template.logo_alto), Image.Resampling.LANCZOS)
                imagen.paste(logo, (template.logo_x, template.logo_y), logo if logo.mode == 'RGBA' else None)
            except Exception as e:
                logger.warning(f"Error al cargar logo: {e}")
        
        # Cargar y colocar foto del empleado
        if template.mostrar_foto and foto_path and Path(foto_path).exists():
            try:
                foto = Image.open(foto_path)
                foto = foto.resize((template.foto_ancho, template.foto_alto), Image.Resampling.LANCZOS)
                # Crear máscara circular opcional (por ahora rectangular)
                imagen.paste(foto, (template.foto_x, template.foto_y))
            except Exception as e:
                logger.warning(f"Error al cargar foto del empleado: {e}")
        
        # Intentar cargar fuentes
        try:
            nombre_font = ImageFont.truetype(f"{template.nombre_fuente.lower()}.ttf", template.nombre_tamaño)
        except:
            try:
                nombre_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", template.nombre_tamaño)
            except:
                nombre_font = ImageFont.load_default()
        
        try:
            cedula_font = ImageFont.truetype(f"{template.cedula_fuente.lower()}.ttf", template.cedula_tamaño)
        except:
            try:
                cedula_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", template.cedula_tamaño)
            except:
                cedula_font = ImageFont.load_default()
        
        try:
            cargo_font = ImageFont.truetype(f"{template.cargo_fuente.lower()}.ttf", template.cargo_tamaño)
        except:
            try:
                cargo_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", template.cargo_tamaño)
            except:
                cargo_font = ImageFont.load_default()
        
        try:
            empresa_font = ImageFont.truetype(f"{template.empresa_fuente.lower()}.ttf", template.empresa_tamaño)
        except:
            try:
                empresa_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", template.empresa_tamaño)
            except:
                empresa_font = ImageFont.load_default()
        
        try:
            web_font = ImageFont.truetype(f"{template.web_fuente.lower()}.ttf", template.web_tamaño)
        except:
            try:
                web_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", template.web_tamaño)
            except:
                web_font = ImageFont.load_default()
        
        # Dibujar nombre
        if template.mostrar_nombre and nombre_empleado:
            draw.text(
                (template.nombre_x, template.nombre_y),
                nombre_empleado.upper(),
                fill=template.nombre_color,
                font=nombre_font
            )
        
        # Dibujar cédula
        if template.mostrar_cedula and cedula:
            draw.text(
                (template.cedula_x, template.cedula_y),
                f"Cédula: {cedula}",
                fill=template.cedula_color,
                font=cedula_font
            )
        
        # Dibujar cargo
        if template.mostrar_cargo and cargo:
            draw.text(
                (template.cargo_x, template.cargo_y),
                cargo,
                fill=template.cargo_color,
                font=cargo_font
            )
        
        # Dibujar información de empresa
        if template.mostrar_empresa and empresa:
            draw.text(
                (template.empresa_x, template.empresa_y),
                empresa,
                fill=template.empresa_color,
                font=empresa_font
            )
        
        # Dibujar web
        if template.mostrar_web and web:
            draw.text(
                (template.web_x, template.web_y),
                web,
                fill=template.web_color,
                font=web_font
            )
        
        # Colocar código de barras
        if codigo_barras_path and Path(codigo_barras_path).exists():
            try:
                codigo_img = Image.open(codigo_barras_path)
                codigo_img = codigo_img.resize(
                    (template.codigo_barras_ancho, template.codigo_barras_alto),
                    Image.Resampling.LANCZOS
                )
                imagen.paste(codigo_img, (template.codigo_barras_x, template.codigo_barras_y))
                
                # Mostrar número del código si está habilitado
                if template.mostrar_numero_codigo:
                    try:
                        numero_font = ImageFont.truetype(f"{template.numero_codigo_fuente.lower()}.ttf", template.numero_codigo_tamaño)
                    except:
                        try:
                            numero_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", template.numero_codigo_tamaño)
                        except:
                            numero_font = ImageFont.load_default()
                    
                    # Extraer número del código desde el nombre del archivo o usar un valor por defecto
                    numero_codigo = Path(codigo_barras_path).stem.split('_')[-1] if '_' in Path(codigo_barras_path).stem else "12345678"
                    draw.text(
                        (template.codigo_barras_x, template.codigo_barras_y + template.codigo_barras_alto + 5),
                        numero_codigo,
                        fill=template.numero_codigo_color,
                        font=numero_font
                    )
            except Exception as e:
                logger.warning(f"Error al cargar código de barras: {e}")
        
        return imagen
    
    def guardar_carnet(self, imagen: Image.Image, ruta_salida: Path, formato: str = "PNG") -> bool:
        """
        Guarda el carnet renderizado
        
        Args:
            imagen: Imagen del carnet
            ruta_salida: Ruta donde guardar
            formato: Formato de imagen (PNG, JPG, etc.)
            
        Returns:
            True si se guardó correctamente
        """
        try:
            if formato.upper() == "PNG":
                imagen.save(ruta_salida, "PNG", dpi=(300, 300))
            elif formato.upper() == "JPG" or formato.upper() == "JPEG":
                imagen.save(ruta_salida, "JPEG", quality=95, dpi=(300, 300))
            else:
                imagen.save(ruta_salida, formato.upper(), dpi=(300, 300))
            return True
        except Exception as e:
            logger.error(f"Error al guardar carnet: {e}")
            return False

