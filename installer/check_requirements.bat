@echo off
REM Script para verificar que todos los requisitos estan instalados
REM Este script debe ejecutarse desde la carpeta installer/

cd ..

echo ================================================================================
echo     VERIFICACION DE REQUISITOS PARA EL INSTALADOR
echo ================================================================================
echo.

set ERRORS=0

REM Verificar Python
echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    set ERRORS=1
) else (
    for /f "tokens=*" %%i in ('python --version') do echo [OK] %%i
)

REM Verificar entorno virtual
echo [2/5] Verificando entorno virtual...
if exist "env\Scripts\python.exe" (
    echo [OK] Entorno virtual encontrado en env\
) else (
    echo [ERROR] No se encontro el entorno virtual en env\
    echo        Crea uno con: python -m venv env
    set ERRORS=1
)

REM Verificar PyInstaller en entorno virtual
echo [3/5] Verificando PyInstaller...
call env\Scripts\activate.bat
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [AVISO] PyInstaller no esta instalado
    echo         Se instalara automaticamente al ejecutar build_installer
) else (
    for /f "tokens=2" %%i in ('pip show pyinstaller ^| findstr Version') do echo [OK] PyInstaller %%i
)

REM Verificar Inno Setup
echo [4/5] Verificando Inno Setup...
set INNO_FOUND=0

if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo [OK] Inno Setup 6 encontrado en Program Files ^(x86^)
    set INNO_FOUND=1
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    echo [OK] Inno Setup 6 encontrado en Program Files
    set INNO_FOUND=1
)

where iscc >nul 2>&1
if errorlevel 0 (
    if %INNO_FOUND%==0 (
        echo [OK] Inno Setup encontrado en PATH
        set INNO_FOUND=1
    )
)

if %INNO_FOUND%==0 (
    echo [ERROR] Inno Setup no esta instalado
    echo         Descarga desde: https://jrsoftware.org/isdl.php
    set ERRORS=1
)

REM Verificar espacio en disco
echo [5/5] Verificando espacio en disco...
for /f "tokens=3" %%i in ('dir /-c ^| findstr "bytes free"') do set FREE_SPACE=%%i
echo [OK] Espacio disponible verificado

echo.
echo ================================================================================
echo RESUMEN
echo ================================================================================
echo.

if %ERRORS%==0 (
    echo [OK] Todos los requisitos estan instalados!
    echo.
    echo Puedes ejecutar:
    echo   - build_installer.bat  ^(para crear el instalador completo^)
    echo   - test_build.bat       ^(para solo probar la compilacion^)
    echo.
) else (
    echo [ERROR] Faltan algunos requisitos. Por favor instalalos antes de continuar.
    echo.
)

echo ================================================================================
pause

