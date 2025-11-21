@echo off
REM Script de instalacion automatica de Poppler para Windows
REM Requerido para la verificacion OCR de archivos PDF

setlocal enabledelayedexpansion

REM Deshabilitar cierre automatico en caso de error
set "ERROR_OCCURRED=0"
set "INSTALL_SUCCESS=0"

REM Cambiar al directorio del script para evitar problemas con rutas relativas
cd /d "%~dp0" 2>nul || cd /d "%~dp0"

echo ========================================
echo   INSTALADOR DE POPPLER PARA WINDOWS
echo ========================================
echo.
echo Este script instalara Poppler automaticamente.
echo Poppler es necesario para la verificacion OCR de archivos PDF.
echo.
echo Presiona cualquier tecla para continuar...
pause >nul 2>&1
echo.

REM Verificar si se ejecuta como administrador
echo Verificando privilegios de administrador...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Este script requiere privilegios de administrador.
    echo.
    echo Por favor, ejecuta este script como administrador:
    echo 1. Clic derecho en el archivo
    echo 2. Selecciona "Ejecutar como administrador"
    echo.
    echo Presiona cualquier tecla para salir...
    pause >nul
    exit /b 1
)
echo [OK] Privilegios de administrador confirmados.
echo.

echo [1/5] Verificando si Poppler ya esta instalado...
where pdftoppm >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Poppler ya esta instalado en el sistema.
    echo.
    echo Version instalada:
    pdftoppm -v
    echo.
    echo Si deseas reinstalar, primero elimina Poppler del PATH.
    echo.
    echo Presiona cualquier tecla para salir...
    pause >nul
    exit /b 0
)
echo [INFO] Poppler no encontrado en PATH. Continuando con la instalacion...
echo.


REM Definir rutas
set INSTALL_DIR=C:\poppler
set BIN_DIR=%INSTALL_DIR%\bin
set POPPLER_FOUND=0
set POPPLER_SOURCE_DIR=

REM [2/5] Buscar Poppler ya extraido en ubicaciones comunes
echo [2/5] Buscando Poppler ya extraido...
echo.

REM Buscar en Downloads del usuario actual
set USER_PROFILE=%USERPROFILE%
if not defined USER_PROFILE (
    set USER_PROFILE=%HOMEDRIVE%%HOMEPATH%
)

echo Buscando en: %USER_PROFILE%\Downloads...

if exist "%USER_PROFILE%\Downloads\poppler-25.07.0\Library\bin\pdftoppm.exe" (
    set "POPPLER_SOURCE_DIR=%USER_PROFILE%\Downloads\poppler-25.07.0"
    set POPPLER_FOUND=1
    echo [OK] Poppler encontrado en: %POPPLER_SOURCE_DIR%
) else if exist "%USER_PROFILE%\Downloads\poppler-25.07.0\bin\pdftoppm.exe" (
    set "POPPLER_SOURCE_DIR=%USER_PROFILE%\Downloads\poppler-25.07.0"
    set POPPLER_FOUND=1
    echo [OK] Poppler encontrado en: %POPPLER_SOURCE_DIR%
) else (
    REM Buscar cualquier carpeta poppler en Downloads
    if exist "%USER_PROFILE%\Downloads" (
        for /d %%d in ("%USER_PROFILE%\Downloads\poppler-*" 2^>nul) do (
            if exist "%%d\Library\bin\pdftoppm.exe" (
                set "POPPLER_SOURCE_DIR=%%d"
                set POPPLER_FOUND=1
                echo [OK] Poppler encontrado en: %%d
                goto :found_poppler
            ) else if exist "%%d\bin\pdftoppm.exe" (
                set "POPPLER_SOURCE_DIR=%%d"
                set POPPLER_FOUND=1
                echo [OK] Poppler encontrado en: %%d
                goto :found_poppler
            )
        )
    )
    :found_poppler
)

REM Si no se encontro, buscar en otras ubicaciones comunes
if %POPPLER_FOUND% equ 0 (
    echo [INFO] Poppler no encontrado en Downloads. Buscando en otras ubicaciones...
    
    REM Buscar en C:\poppler
    if exist "C:\poppler\bin\pdftoppm.exe" (
        set "POPPLER_SOURCE_DIR=C:\poppler"
        set POPPLER_FOUND=1
        echo [OK] Poppler encontrado en: C:\poppler
    )
    
    REM Buscar en C:\Program Files\poppler
    if %POPPLER_FOUND% equ 0 (
        if exist "C:\Program Files\poppler\bin\pdftoppm.exe" (
            set "POPPLER_SOURCE_DIR=C:\Program Files\poppler"
            set POPPLER_FOUND=1
            echo [OK] Poppler encontrado en: C:\Program Files\poppler
        )
    )
)

REM Si no se encontro, intentar descargar
if %POPPLER_FOUND% equ 0 (
    echo [INFO] Poppler no encontrado localmente. Intentando descargar...
    echo.
    
    REM Definir version y URL de descarga
    set POPPLER_VERSION=25.11.0-0
    set POPPLER_URL=https://github.com/oschwartz10612/poppler-windows/releases/download/v%POPPLER_VERSION%/Release-%POPPLER_VERSION%.zip
    set POPPLER_ZIP=poppler-%POPPLER_VERSION%.zip
    
    echo Descargando Poppler %POPPLER_VERSION%...
    echo URL: %POPPLER_URL%
    echo.
    
    REM Intentar descargar con PowerShell
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%POPPLER_URL%' -OutFile '%POPPLER_ZIP%' -UseBasicParsing}" 2>nul
    
    if not exist "%POPPLER_ZIP%" (
        echo [ERROR] No se pudo descargar Poppler.
        echo.
        echo Por favor, descarga manualmente desde:
        echo https://github.com/oschwartz10612/poppler-windows/releases
        echo.
        echo O extrae Poppler en una de estas ubicaciones:
        echo - %USER_PROFILE%\Downloads\poppler-25.07.0
        echo - C:\poppler
        echo - C:\Program Files\poppler
        echo.
        pause
        exit /b 1
    )
    
    echo [OK] Descarga completada.
    echo.
    
    REM Extraer temporalmente para encontrar la estructura
    set TEMP_EXTRACT=%TEMP%\poppler_extract
    if exist "%TEMP_EXTRACT%" rmdir /s /q "%TEMP_EXTRACT%" 2>nul
    mkdir "%TEMP_EXTRACT%" 2>nul
    
    powershell -Command "Expand-Archive -Path '%POPPLER_ZIP%' -DestinationPath '%TEMP_EXTRACT%' -Force" 2>nul
    
    REM Buscar donde esta el bin
    for /d %%d in ("%TEMP_EXTRACT%\*") do (
        if exist "%%d\Library\bin\pdftoppm.exe" (
            set "POPPLER_SOURCE_DIR=%%d"
            set POPPLER_FOUND=1
            goto :found_extracted
        ) else if exist "%%d\bin\pdftoppm.exe" (
            set "POPPLER_SOURCE_DIR=%%d"
            set POPPLER_FOUND=1
            goto :found_extracted
        )
    )
    :found_extracted
    
    if %POPPLER_FOUND% equ 0 (
        echo [ERROR] No se pudo encontrar la estructura de Poppler en el archivo descargado.
        pause
        exit /b 1
    )
)

echo.

echo [3/5] Copiando archivos a la ubicacion de instalacion...
if exist "%INSTALL_DIR%" (
    echo Eliminando instalacion anterior...
    rmdir /s /q "%INSTALL_DIR%" 2>nul
)

REM Crear directorio de instalacion
mkdir "%INSTALL_DIR%" 2>nul

REM Determinar la ruta del bin en el origen
set SOURCE_BIN_DIR=
if exist "%POPPLER_SOURCE_DIR%\Library\bin\pdftoppm.exe" (
    set "SOURCE_BIN_DIR=%POPPLER_SOURCE_DIR%\Library\bin"
) else if exist "%POPPLER_SOURCE_DIR%\bin\pdftoppm.exe" (
    set "SOURCE_BIN_DIR=%POPPLER_SOURCE_DIR%\bin"
) else (
    echo [ERROR] No se pudo encontrar pdftoppm.exe en: %POPPLER_SOURCE_DIR%
    pause
    exit /b 1
)

REM Copiar archivos
echo Copiando desde: %POPPLER_SOURCE_DIR%
echo Hacia: %INSTALL_DIR%
xcopy "%POPPLER_SOURCE_DIR%" "%INSTALL_DIR%" /E /I /H /Y >nul 2>&1

REM Determinar la estructura y copiar ejecutables a bin
REM Buscar en cualquier subdirectorio que pueda tener la estructura
set POPPLER_BIN_FOUND=0

REM Buscar Library\bin en cualquier subdirectorio
for /d %%d in ("%INSTALL_DIR%\*") do (
    if exist "%%d\Library\bin\pdftoppm.exe" (
        echo Reorganizando estructura (%%d\Library\bin -^> %BIN_DIR%)...
        mkdir "%BIN_DIR%" 2>nul
        copy "%%d\Library\bin\*.*" "%BIN_DIR%\" /Y >nul 2>&1
        echo [OK] Ejecutables copiados a: %BIN_DIR%
        set POPPLER_BIN_FOUND=1
        goto :bin_found
    ) else if exist "%%d\bin\pdftoppm.exe" (
        echo Reorganizando estructura (%%d\bin -^> %BIN_DIR%)...
        mkdir "%BIN_DIR%" 2>nul
        copy "%%d\bin\*.*" "%BIN_DIR%\" /Y >nul 2>&1
        echo [OK] Ejecutables copiados a: %BIN_DIR%
        set POPPLER_BIN_FOUND=1
        goto :bin_found
    )
)

REM Si no se encontro en subdirectorios, buscar directamente
if %POPPLER_BIN_FOUND% equ 0 (
    if exist "%INSTALL_DIR%\Library\bin\pdftoppm.exe" (
        REM Estructura con Library\bin - copiar ejecutables a bin directo
        echo Reorganizando estructura (Library\bin -^> bin)...
        mkdir "%BIN_DIR%" 2>nul
        copy "%INSTALL_DIR%\Library\bin\*.*" "%BIN_DIR%\" /Y >nul 2>&1
        echo [OK] Ejecutables copiados a: %BIN_DIR%
        set POPPLER_BIN_FOUND=1
    ) else if exist "%INSTALL_DIR%\bin\pdftoppm.exe" (
        REM Ya esta en la estructura correcta
        set "BIN_DIR=%INSTALL_DIR%\bin"
        echo [OK] Estructura correcta detectada.
        set POPPLER_BIN_FOUND=1
    )
)

:bin_found

if %POPPLER_BIN_FOUND% equ 0 (
    echo [ERROR] No se pudo encontrar pdftoppm.exe despues de copiar.
    echo Estructura esperada: Library\bin\pdftoppm.exe o bin\pdftoppm.exe
    echo.
    echo Buscando en: %INSTALL_DIR%
    dir "%INSTALL_DIR%" /s /b | findstr /i "pdftoppm.exe"
    pause
    exit /b 1
)

if not exist "%BIN_DIR%\pdftoppm.exe" (
    echo [ERROR] No se pudo encontrar pdftoppm.exe despues de copiar.
    echo Verifica que los archivos se copiaron correctamente.
    pause
    exit /b 1
)

echo [OK] Archivos copiados a: %INSTALL_DIR%
echo.

REM Limpiar archivo ZIP descargado si existe
if defined POPPLER_ZIP (
    if exist "%POPPLER_ZIP%" (
        echo Eliminando archivo ZIP temporal...
        del "%POPPLER_ZIP%" >nul 2>&1
    )
)

REM Limpiar extraccion temporal si existe
if defined TEMP_EXTRACT (
    if exist "%TEMP_EXTRACT%" (
        echo Eliminando archivos temporales de extraccion...
        rmdir /s /q "%TEMP_EXTRACT%" >nul 2>&1
    )
)

echo [4/5] Agregando Poppler al PATH del sistema...
echo.

REM Obtener el PATH actual del sistema
set CURRENT_PATH=
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do (
    set "CURRENT_PATH=%%b"
)

if not defined CURRENT_PATH (
    echo [ERROR] No se pudo leer el PATH del sistema.
    echo.
    echo Presiona cualquier tecla para salir...
    pause >nul 2>&1
    exit /b 1
)

REM Verificar si ya esta en el PATH
echo %CURRENT_PATH% | findstr /C:"%BIN_DIR%" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Poppler ya esta en el PATH del sistema.
) else (
    echo Agregando %BIN_DIR% al PATH del sistema...
    REM Agregar al PATH del sistema
    setx PATH "%CURRENT_PATH%;%BIN_DIR%" /M >nul 2>&1
    
    if %errorLevel% equ 0 (
        echo [OK] Poppler agregado al PATH del sistema.
        echo.
        echo NOTA: Es posible que necesites reiniciar la aplicacion o
        echo abrir una nueva ventana de CMD para que los cambios surtan efecto.
    ) else (
        echo [ERROR] No se pudo agregar Poppler al PATH del sistema.
        echo.
        echo Puedes agregarlo manualmente:
        echo 1. Win + X -^> Sistema
        echo 2. Configuracion avanzada del sistema
        echo 3. Variables de entorno
        echo 4. Agregar: %BIN_DIR%
        echo.
        set "ERROR_OCCURRED=1"
    )
)

echo.

echo [5/5] Verificando instalacion...
echo.

REM Actualizar PATH en la sesion actual
set "PATH=%PATH%;%BIN_DIR%"

REM Verificar instalacion
echo Verificando que pdftoppm.exe funciona...
if not exist "%BIN_DIR%\pdftoppm.exe" (
    echo [ERROR] El archivo pdftoppm.exe no existe en: %BIN_DIR%
    echo.
    set INSTALL_SUCCESS=0
    set "ERROR_OCCURRED=1"
) else (
    "%BIN_DIR%\pdftoppm.exe" -v >nul 2>&1
    if %errorLevel% equ 0 (
        echo [OK] Poppler instalado correctamente!
        echo.
        echo Version instalada:
        "%BIN_DIR%\pdftoppm.exe" -v 2>&1
        echo.
        echo ========================================
        echo   INSTALACION COMPLETADA EXITOSAMENTE
        echo ========================================
        echo.
        echo Poppler esta instalado en: %INSTALL_DIR%
        echo Binarios en: %BIN_DIR%
        echo.
        echo IMPORTANTE:
        echo - Reinicia la aplicacion para que detecte Poppler
        echo - O abre una nueva ventana de CMD/PowerShell
        echo - El PATH del sistema ha sido actualizado
        echo.
        set INSTALL_SUCCESS=1
    ) else (
        echo [ERROR] La verificacion fallo.
        echo.
        echo Verifica manualmente:
        echo 1. Que el archivo existe: %BIN_DIR%\pdftoppm.exe
        echo 2. Que tienes permisos para ejecutarlo
        echo.
        set INSTALL_SUCCESS=0
        set "ERROR_OCCURRED=1"
    )
)

REM Limpiar archivo ZIP descargado si existe
if defined POPPLER_ZIP (
    if exist "%POPPLER_ZIP%" (
        echo.
        echo Eliminando archivo ZIP temporal...
        del "%POPPLER_ZIP%" >nul 2>&1
    )
)

echo.
echo ========================================
if defined INSTALL_SUCCESS (
    if !INSTALL_SUCCESS! equ 1 (
        echo   RESULTADO: INSTALACION EXITOSA
    ) else (
        echo   RESULTADO: INSTALACION CON ERRORES
    )
) else if defined ERROR_OCCURRED (
    if !ERROR_OCCURRED! equ 1 (
        echo   RESULTADO: INSTALACION CON ERRORES
    ) else (
        echo   RESULTADO: INSTALACION COMPLETADA
    )
) else (
    echo   RESULTADO: INSTALACION COMPLETADA
)
echo ========================================
echo.
echo ========================================
echo Presiona cualquier tecla para cerrar...
echo ========================================
pause
if %errorLevel% neq 0 (
    echo.
    echo Esperando 5 segundos antes de cerrar...
    timeout /t 5
)
endlocal

