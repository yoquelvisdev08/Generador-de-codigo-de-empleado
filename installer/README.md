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

---

## 📋 Requisitos

### Para crear el instalador (tu PC):
- Python 3.10+ (ya instalado)
- Entorno virtual activo
- Inno Setup 6.0+ → [Descargar](https://jrsoftware.org/isdl.php)

### Para el usuario final:
- Windows 10/11 (64-bit)
- NO necesita Python ni dependencias

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
