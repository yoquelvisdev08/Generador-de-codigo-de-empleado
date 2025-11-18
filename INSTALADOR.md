# 📦 Sistema de Instalación para Windows

## Crear Instalador Profesional

Todos los archivos necesarios para crear un instalador de Windows están en la carpeta **`installer/`**

---

## ⚡ Inicio Rápido

### 1. Instalar Inno Setup (solo la primera vez)
- Descarga: https://jrsoftware.org/isdl.php
- Instala con opciones predeterminadas

### 2. Crear el Instalador

**PowerShell:**
```powershell
cd installer
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build_installer.ps1
```

**CMD:**
```cmd
cd installer
build_installer.bat
```

### 3. Resultado

Tu instalador estará en:
```
installer\output_installer\GeneradorCodigosCarnet_Setup_v1.0.0.exe
```

---

## 📚 Documentación Completa

Toda la documentación está en la carpeta **`installer/`**:

- **`installer/README.md`** - Documentación principal completa
- **`installer/INICIO_RAPIDO.txt`** - Instrucciones ultra-rápidas
- **`installer/RESUMEN_INSTALADOR.md`** - Visión general
- **`installer/COMO_CREAR_INSTALADOR.md`** - Guía paso a paso
- **`installer/INSTALLER_README.md`** - Documentación técnica avanzada
- **`installer/TEST_INSTALADOR.md`** - Plan de pruebas

---

## 🎯 Características del Instalador

✅ Ejecutable completo sin necesidad de Python  
✅ Asistente de instalación en español  
✅ Términos y condiciones  
✅ Accesos directos (escritorio + menú inicio)  
✅ Registro en Windows  
✅ Desinstalador completo  
✅ ~150-250 MB (todo incluido)

---

## ⏱️ Tiempo Estimado

- **Primera vez:** 15-20 minutos (incluyendo instalación de Inno Setup)
- **Siguientes veces:** 7-10 minutos

---

## 📞 Soporte

Para más información, consulta **`installer/README.md`**

---

**© 2025 YoquelvisDev**

