@echo off
REM Script de compilación e instalación para Windows
REM Este script automatiza todo el proceso de creación del instalador

echo ================================================================================
echo     GENERADOR DE CODIGOS DE CARNET - COMPILADOR DE INSTALADOR
echo ================================================================================
echo.

REM Verificar que estamos en el directorio correcto
REM Este script debe ejecutarse desde la carpeta installer/
cd ..
if not exist "main.py" (
    echo ERROR: No se encontro main.py
    echo Por favor ejecute este script desde la carpeta installer del proyecto
    pause
    exit /b 1
)

echo [1/6] Verificando entorno virtual...
REM Buscar entorno virtual (env312 o env)
if exist "env312\Scripts\activate.bat" (
    set ENV_PATH=env312
) else if exist "env\Scripts\activate.bat" (
    set ENV_PATH=env
) else (
    echo ERROR: No se encontro el entorno virtual en env312\ o env\
    echo Por favor cree el entorno virtual primero con: python -m venv env312
    pause
    exit /b 1
)

echo Entorno virtual encontrado: %ENV_PATH%
echo [2/6] Activando entorno virtual...
call %ENV_PATH%\Scripts\activate.bat

echo [3/6] Verificando instalacion de PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller no esta instalado. Instalando...
    pip install pyinstaller
)

echo [4/6] Limpiando y recreando directorios de compilacion...

REM Eliminar completamente las carpetas existentes
if exist "build" (
    echo Eliminando directorio build...
    rmdir /s /q build
    timeout /t 1 /nobreak >nul
)
if exist "dist" (
    echo Eliminando directorio dist...
    rmdir /s /q dist
    timeout /t 1 /nobreak >nul
)
if exist "installer\output_installer" (
    echo Eliminando directorio output_installer...
    rmdir /s /q installer\output_installer
    timeout /t 1 /nobreak >nul
)

REM Crear carpetas limpias de nuevo
echo Creando directorios limpios...
mkdir build 2>nul
mkdir dist 2>nul
mkdir installer\output_installer 2>nul

echo Limpieza completada.

echo [5/6] Compilando aplicacion con PyInstaller...
echo Esto puede tardar varios minutos...
pyinstaller installer\build_spec.spec --noconfirm
if errorlevel 1 (
    echo ERROR: La compilacion con PyInstaller fallo
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo COMPILACION EXITOSA!
echo ================================================================================
echo.
echo El ejecutable se encuentra en: dist\GeneradorCodigosCarnet\
echo.
echo [6/6] Para crear el instalador, necesita Inno Setup instalado.
echo.
echo PASOS SIGUIENTES:
echo.
echo 1. Instale Inno Setup desde: https://jrsoftware.org/isdl.php
echo 2. Abra el archivo: installer_script.iss con Inno Setup
echo 3. Compile el script (Build ^> Compile)
echo 4. El instalador se generara en: output_installer\
echo.
echo ALTERNATIVA: Si tiene Inno Setup instalado con ISCC en el PATH:
echo.
echo    Ejecute: iscc installer\installer_script.iss
echo.
echo ================================================================================
echo.

REM Intentar compilar con Inno Setup si está disponible
where iscc >nul 2>&1
if errorlevel 1 (
    echo NOTA: Inno Setup Compiler (iscc) no esta en el PATH
    echo Abra installer_script.iss manualmente con Inno Setup
) else (
    echo.
    echo Se detecto Inno Setup Compiler en el sistema.
    set /p COMPILE_ISS="¿Desea compilar el instalador ahora? (S/N): "
    if /i "%COMPILE_ISS%"=="S" (
        echo.
        echo Compilando instalador con Inno Setup...
        iscc installer\installer_script.iss
        if errorlevel 1 (
            echo ERROR: La compilacion del instalador fallo
            pause
            exit /b 1
        ) else (
            echo.
            echo ================================================================================
            echo INSTALADOR CREADO EXITOSAMENTE!
            echo ================================================================================
            echo.
            echo El instalador se encuentra en: installer\output_installer\
            echo.
        )
    )
)

echo Presione cualquier tecla para finalizar...
pause >nul

