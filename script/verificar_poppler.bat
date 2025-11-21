@echo off
REM Script para verificar si Poppler esta instalado correctamente

echo ========================================
echo   VERIFICACION DE POPPLER
echo ========================================
echo.

REM Verificar si pdftoppm esta en PATH
echo [1/3] Verificando si Poppler esta en PATH...
where pdftoppm >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Poppler encontrado en PATH!
    echo.
    echo Version instalada:
    pdftoppm -v
    echo.
) else (
    echo [ERROR] Poppler NO esta en PATH.
    echo.
)

REM Verificar si existe en la ubicacion de instalacion
echo [2/3] Verificando instalacion en C:\poppler...
if exist "C:\poppler\bin\pdftoppm.exe" (
    echo [OK] Poppler encontrado en: C:\poppler\bin\
    echo.
    echo Version:
    "C:\poppler\bin\pdftoppm.exe" -v
    echo.
) else (
    echo [INFO] Poppler no encontrado en C:\poppler\bin\
    echo.
)

REM Verificar PATH del sistema
echo [3/3] Verificando PATH del sistema...
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "CURRENT_PATH=%%b"

echo %CURRENT_PATH% | findstr /C:"C:\poppler\bin" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] C:\poppler\bin esta en el PATH del sistema.
) else (
    echo [ERROR] C:\poppler\bin NO esta en el PATH del sistema.
    echo.
    echo Para agregarlo manualmente:
    echo 1. Win + X -^> Sistema
    echo 2. Configuracion avanzada del sistema
    echo 3. Variables de entorno
    echo 4. Agregar: C:\poppler\bin
)

echo.
echo ========================================
echo   RESUMEN
echo ========================================
echo.

REM Verificar si todo esta bien
where pdftoppm >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Poppler esta correctamente instalado y configurado!
    echo.
    echo Puedes usar Poppler desde cualquier ubicacion.
) else (
    if exist "C:\poppler\bin\pdftoppm.exe" (
        echo [ADVERTENCIA] Poppler esta instalado pero no en PATH.
        echo.
        echo Solucion:
        echo 1. Reinicia la aplicacion
        echo 2. O abre una nueva ventana de CMD/PowerShell
        echo 3. O agrega C:\poppler\bin al PATH manualmente
    ) else (
        echo [ERROR] Poppler NO esta instalado.
        echo.
        echo Ejecuta install_poppler.bat como administrador.
    )
)

echo.
echo Presiona cualquier tecla para cerrar...
pause >nul 2>&1
if %errorLevel% neq 0 (
    timeout /t 3
)

