@echo off
REM Script para limpiar el caché de iconos de Windows
REM Esto fuerza a Windows a recargar los iconos

echo ================================================================================
echo     LIMPIADOR DE CACHE DE ICONOS DE WINDOWS
echo ================================================================================
echo.
echo Este script limpiara el cache de iconos de Windows para que se vea
echo correctamente el icono del ejecutable.
echo.
echo IMPORTANTE: Esto cerrara el Explorador de Windows temporalmente.
echo.
pause

echo.
echo [1/4] Cerrando el Explorador de Windows...
taskkill /f /im explorer.exe

echo [2/4] Limpiando cache de iconos...
timeout /t 2 /nobreak >nul

REM Eliminar caché de iconos
cd /d %userprofile%\AppData\Local
if exist IconCache.db (
    del /f /q IconCache.db
    echo Cache de iconos eliminado: IconCache.db
)

if exist Microsoft\Windows\Explorer\*.db (
    del /f /q Microsoft\Windows\Explorer\*.db
    echo Cache de iconos eliminado: Microsoft\Windows\Explorer\
)

echo [3/4] Esperando 2 segundos...
timeout /t 2 /nobreak >nul

echo [4/4] Reiniciando el Explorador de Windows...
start explorer.exe

echo.
echo ================================================================================
echo LIMPIEZA COMPLETADA
echo ================================================================================
echo.
echo El Explorador de Windows se ha reiniciado.
echo Ahora ve a la carpeta dist\GeneradorCodigosCarnet\ y el icono deberia verse.
echo.
echo Si aun no se ve:
echo   1. Presiona F5 para refrescar la carpeta
echo   2. Reinicia la PC
echo.
pause


