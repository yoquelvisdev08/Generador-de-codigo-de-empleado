# Sistema de Instalación - Generador de Códigos de Carnet

Sistema para crear un instalador profesional de Windows (.exe) para la aplicación.

---

## 🚀 Uso Rápido

### Método Automático (Recomendado)

**PowerShell:**
```powershell
cd installer
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build_installer.ps1
```

**CMD:**
```cmd
cd installer
.\build_installer.bat
```

### Método Manual

1. **Compilar aplicación:**
   ```cmd
   cd ..
   pyinstaller installer\build_spec.spec --noconfirm
   ```

2. **Crear instalador con Inno Setup:**
   - Abre `installer_script.iss` con Inno Setup
   - Build > Compile
   - O ejecuta: `iscc installer\installer_script.iss`

---

## 📦 Resultado

El instalador se genera en:
```
installer\output_installer\GeneradorCodigosCarnet_Setup_v1.0.0.exe
```

Tamaño: ~150-250 MB (todo incluido, listo para distribuir)

### Características del Instalador

- **Instalación automática de Tesseract OCR**: El instalador verifica si Tesseract está instalado y, si no lo está, lo descarga e instala automáticamente durante el proceso de instalación.
- **Instalación automática de Poppler**: El instalador incluye Poppler empaquetado y lo instala automáticamente en `C:\Program Files\poppler` si no está presente en el sistema.
- **Sin dependencias manuales**: El usuario no necesita instalar Python, Tesseract u otras dependencias manualmente.
- **Instalación silenciosa**: Tesseract se instala de forma silenciosa con los idiomas Spanish y English pre-seleccionados.
- **Verificación automática**: El instalador verifica que Tesseract y Poppler se hayan instalado correctamente antes de completar la instalación.
- **Scripts de instalación incluidos**: Los scripts `install_poppler.bat` y `verificar_poppler.bat` están incluidos en la instalación para facilitar la instalación manual de Poppler si es necesario.
- **Incluye todas las funcionalidades**: Generación de códigos de barras, códigos de servicio, carnets personalizados, verificación OCR, exportación a Excel, y más.

---

## 📋 Requisitos

### Para crear el instalador (tu PC):
- Python 3.10+ (ya instalado)
- Entorno virtual activo
- Inno Setup 6.0+ → [Descargar](https://jrsoftware.org/isdl.php)
- **Inno Dependency Installer (CodeDependencies.iss)** → [Descargar](https://github.com/DomGries/InnoDependencyInstaller) (opcional pero recomendado)
  - Ya incluido en la carpeta `installer/InnoDependencyInstaller-master/`
  - El script lo detectará automáticamente
  - Si no está disponible, el instalador funcionará pero mostrará un mensaje para instalar Tesseract manualmente

### Para el usuario final:
- Windows 10/11 (64-bit)
- NO necesita Python ni dependencias
- **Tesseract OCR**: Se instalará automáticamente durante la instalación si no está presente
  - El instalador verificará si Tesseract está instalado
  - Si no está instalado, lo descargará e instalará automáticamente
  - Se instalarán los idiomas Spanish y English automáticamente
  - Requiere conexión a Internet para la descarga automática
- **Poppler (opcional)**: Necesario solo para verificación OCR de archivos PDF
  - El instalador verificará si Poppler está instalado
  - Si no está instalado, puede instalarlo después usando `install_poppler.bat` (incluido en la aplicación)
  - Ejecute `install_poppler.bat` como administrador para instalación automática
  - O descargue manualmente desde: https://github.com/oschwartz10612/poppler-windows/releases
  - Sin Poppler, la verificación OCR funcionará solo para PNG, no para PDFs

---

## 📁 Archivos de esta Carpeta

### Esenciales (NO borrar):
- `build_spec.spec` - Configuración de PyInstaller
- `installer_script.iss` - Script de Inno Setup
- `LICENSE.txt` - Términos y condiciones (EULA)
- `README_INSTALLER.txt` - Info pre-instalación
- `env.template` - Template de configuración
- `.gitignore` - Ignorar archivos generados

### Scripts útiles:
- `build_installer.bat` - Script completo (CMD)
- `build_installer.ps1` - Script completo (PowerShell)
- `test_build.bat` - Prueba rápida del ejecutable
- `check_requirements.bat` - Verifica requisitos

### Generado al compilar:
- `output_installer/` - Contiene el instalador final

---

## 🔧 Solución de Problemas

### Error: "PyInstaller no encontrado"
```cmd
pip install pyinstaller
```

### Error: "No se puede ejecutar el script" (PowerShell)
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Error: "Inno Setup no encontrado"
Instalar desde: https://jrsoftware.org/isdl.php

### Error: "CodeDependencies.iss no encontrado" o descarga de Tesseract falla
El instalador intentará descargar Tesseract OCR automáticamente, pero requiere `CodeDependencies.iss`:
1. El archivo ya debería estar en `installer/InnoDependencyInstaller-master/CodeDependencies.iss`
2. Si no está disponible, el instalador funcionará pero el usuario deberá instalar Tesseract manualmente
3. El script detectará automáticamente si `CodeDependencies.iss` está disponible

### El ejecutable no abre
1. Compilar con `console=True` en `build_spec.spec` (línea 109)
2. Ver errores en la consola
3. Verificar dependencias: `pip list`

---

## 🔄 Actualizar Versión

Para crear una nueva versión:

1. Edita `installer_script.iss` línea 7:
   ```ini
   #define MyAppVersion "1.1.0"  ← Cambiar aquí
   ```

2. Recompila:
   ```cmd
   cd installer
   .\build_installer.bat
   ```

---

## 📊 Tiempos Estimados

| Acción | Tiempo |
|--------|--------|
| Instalar Inno Setup (primera vez) | 5 min |
| Compilar con PyInstaller | 5-10 min |
| Crear instalador con Inno Setup | 2-3 min |
| **Total** | **12-18 min** |

---

## 📞 Soporte

**Desarrollador:** YoquelvisDev  
**GitHub:** https://github.com/yoquelvisdev

---

**© 2025 YoquelvisDev**
