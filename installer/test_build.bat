@echo off
REM Script de prueba rápida del ejecutable antes de crear el instalador
REM Este script compila la aplicación y la prueba localmente

echo ================================================================================
echo     PRUEBA RAPIDA DE COMPILACION - Generador de Codigos de Carnet
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

echo [1/5] Verificando entorno virtual...
if not exist "env\Scripts\activate.bat" (
    echo ERROR: No se encontro el entorno virtual en env\
    pause
    exit /b 1
)

echo [2/5] Activando entorno virtual...
call env\Scripts\activate.bat

echo [3/5] Limpiando compilaciones anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo [4/5] Compilando con PyInstaller...
echo Esto puede tardar varios minutos, por favor espere...
echo.
pyinstaller installer\build_spec.spec --noconfirm
if errorlevel 1 (
    echo.
    echo ERROR: La compilacion fallo
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo COMPILACION EXITOSA!
echo ================================================================================
echo.
echo [5/5] Probando el ejecutable...
echo.
echo IMPORTANTE: Pruebe las siguientes funciones:
echo   1. La aplicacion abre correctamente
echo   2. Los logos e iconos se ven
echo   3. Puede crear un usuario administrador
echo   4. Puede hacer login
echo   5. Puede generar un codigo de barras
echo.
echo Presione cualquier tecla para ejecutar la aplicacion...
pause >nul

cd dist\GeneradorCodigosCarnet
start GeneradorCodigosCarnet.exe
cd ..\..

echo.
echo La aplicacion se esta ejecutando...
echo.
echo Si todo funciona correctamente:
echo   - Cierre la aplicacion
echo   - Ejecute build_installer.bat para crear el instalador completo
echo.
echo Si hay errores:
echo   - Revise los mensajes de error en la consola de la aplicacion
echo   - Verifique que todas las dependencias esten instaladas
echo   - Consulte INSTALLER_README.md para solucion de problemas
echo.
pause

