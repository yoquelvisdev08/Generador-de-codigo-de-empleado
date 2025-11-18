"""
Crear ICO válido para PyInstaller - Método simple y robusto
"""
from PIL import Image
import os

def create_ico_simple(png_size=256):
    """Crea un ICO de una sola resolución - PyInstaller lo escalará"""
    
    assets_dir = os.path.dirname(os.path.abspath(__file__))
    png_file = f'logo_{png_size}x{png_size}.png'
    png_path = os.path.join(assets_dir, png_file)
    ico_path = os.path.join(assets_dir, 'logo.ico')
    
    print("="*70)
    print(" "*20 + "CREAR ICO PARA PYINSTALLER")
    print("="*70)
    print()
    
    if not os.path.exists(png_path):
        print(f"[ERROR] No existe: {png_file}")
        return False
    
    print(f"Cargando: {png_file}")
    img = Image.open(png_path)
    
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    print(f"  Tamaño: {img.size}")
    print(f"  Modo: {img.mode}")
    print()
    
    # Eliminar ICO anterior
    if os.path.exists(ico_path):
        os.remove(ico_path)
        print("[OK] ICO anterior eliminado")
    
    print(f"Guardando como ICO ({png_size}x{png_size})...")
    
    try:
        # Guardar ICO - método más simple posible
        img.save(ico_path, format='ICO')
        
        file_size = os.path.getsize(ico_path)
        
        print()
        print(f"[OK] ICO creado: logo.ico")
        print(f"[OK] Tamaño: {file_size:,} bytes ({file_size/1024:.2f} KB)")
        
        # Verificar que sea válido
        test = Image.open(ico_path)
        print(f"[OK] Verificado - Resolución: {test.size}")
        test.close()
        
        if file_size > 5000:
            print("[OK] Tamaño excelente para PyInstaller")
            return True
        elif file_size > 1000:
            print("[OK] Tamaño aceptable")
            return True
        else:
            print("[ADVERTENCIA] ICO muy pequeño")
            return False
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print()
    
    # Intentar con 256, luego 128, luego 64
    for size in [256, 128, 64]:
        if create_ico_simple(size):
            print()
            print("="*70)
            print(" "*28 + "EXITOSO")
            print("="*70)
            print()
            print("AHORA RECOMPILA:")
            print()
            print("  cd installer")
            print("  .\\build_installer.bat")
            print()
            print("Busca en la salida de compilación:")
            print("  [INFO] Icono existe: True")
            print("  INFO: Copying icon to EXE")
            print()
            return
        print()
    
    print("="*70)
    print(" "*30 + "FALLO")
    print("="*70)

if __name__ == "__main__":
    main()

