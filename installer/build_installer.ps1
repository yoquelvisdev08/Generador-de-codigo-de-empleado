# Script de PowerShell para compilar e instalar
# Este script es una alternativa al .bat con mejor manejo de errores

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "    GENERADOR DE CODIGOS DE CARNET - COMPILADOR DE INSTALADOR" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Funcion para escribir mensajes de error
function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "ERROR: $Message" -ForegroundColor Red
}

# Funcion para escribir mensajes de exito
function Write-SuccessMsg {
    param([string]$Message)
    Write-Host "OK: $Message" -ForegroundColor Green
}

# Funcion para escribir mensajes de informacion
function Write-InfoMsg {
    param([string]$Message)
    Write-Host "INFO: $Message" -ForegroundColor Yellow
}

# Verificar que estamos en el directorio correcto
# Este script debe ejecutarse desde la carpeta installer/
Set-Location ..
if (-not (Test-Path "main.py")) {
    Write-ErrorMsg "No se encontro main.py"
    Write-Host "Por favor ejecute este script desde la carpeta installer del proyecto"
    Read-Host "Presione Enter para salir"
    exit 1
}

Write-Host "[1/6] Verificando entorno virtual..." -ForegroundColor Cyan
if (-not (Test-Path "env\Scripts\Activate.ps1")) {
    Write-ErrorMsg "No se encontro el entorno virtual en env\"
    Write-Host "Por favor cree el entorno virtual primero con: python -m venv env"
    Read-Host "Presione Enter para salir"
    exit 1
}
Write-SuccessMsg "Entorno virtual encontrado"

Write-Host "[2/6] Activando entorno virtual..." -ForegroundColor Cyan
& "env\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "No se pudo activar el entorno virtual"
    Read-Host "Presione Enter para salir"
    exit 1
}
Write-SuccessMsg "Entorno virtual activado"

Write-Host "[3/6] Verificando instalacion de PyInstaller..." -ForegroundColor Cyan
$pyinstallerInstalled = pip show pyinstaller 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-InfoMsg "PyInstaller no esta instalado. Instalando..."
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "No se pudo instalar PyInstaller"
        Read-Host "Presione Enter para salir"
        exit 1
    }
}
Write-SuccessMsg "PyInstaller esta instalado"

Write-Host "[4/6] Limpiando compilaciones anteriores..." -ForegroundColor Cyan
$dirsToClean = @("build", "dist", "output_installer")
foreach ($dir in $dirsToClean) {
    if (Test-Path $dir) {
        Write-InfoMsg "Eliminando directorio $dir..."
        Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
Write-SuccessMsg "Limpieza completada"

Write-Host "[5/6] Compilando aplicacion con PyInstaller..." -ForegroundColor Cyan
Write-InfoMsg "Esto puede tardar varios minutos..."
Write-Host ""

pyinstaller installer\build_spec.spec --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "La compilacion con PyInstaller fallo"
    Read-Host "Presione Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "COMPILACIÓN EXITOSA!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
Write-SuccessMsg "El ejecutable se encuentra en: dist\GeneradorCodigosCarnet\"
Write-Host ""

Write-Host "[6/6] Verificando Inno Setup..." -ForegroundColor Cyan

# Buscar Inno Setup en ubicaciones comunes
$innoSetupPaths = @(
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 5\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 5\ISCC.exe"
)

$isccPath = $null
foreach ($path in $innoSetupPaths) {
    if (Test-Path $path) {
        $isccPath = $path
        break
    }
}

# Tambien verificar si esta en el PATH
if (-not $isccPath) {
    $isccInPath = Get-Command iscc -ErrorAction SilentlyContinue
    if ($isccInPath) {
        $isccPath = $isccInPath.Source
    }
}

if (-not $isccPath) {
    Write-Host ""
    Write-InfoMsg "Inno Setup no esta instalado o no se encuentra en el PATH"
    Write-Host ""
    Write-Host "PASOS SIGUIENTES:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Instale Inno Setup desde: https://jrsoftware.org/isdl.php" -ForegroundColor White
    Write-Host "2. Abra el archivo: installer_script.iss con Inno Setup" -ForegroundColor White
    Write-Host "3. Compile el script (Build > Compile)" -ForegroundColor White
    Write-Host "4. El instalador se generara en: output_installer\" -ForegroundColor White
    Write-Host ""
} else {
    Write-SuccessMsg "Inno Setup encontrado en: $isccPath"
    Write-Host ""
    $compile = Read-Host "¿Desea compilar el instalador ahora? (S/N)"
    
    if ($compile -eq "S" -or $compile -eq "s") {
        Write-Host ""
        Write-Host "Compilando instalador con Inno Setup..." -ForegroundColor Cyan
        
        & $isccPath "installer\installer_script.iss"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "================================================================================" -ForegroundColor Green
            Write-Host "INSTALADOR CREADO EXITOSAMENTE!" -ForegroundColor Green
            Write-Host "================================================================================" -ForegroundColor Green
            Write-Host ""
            Write-SuccessMsg "El instalador se encuentra en: installer\output_installer\"
            Write-Host ""
            
            # Listar archivos creados
            if (Test-Path "installer\output_installer") {
                $installers = Get-ChildItem "installer\output_installer\*.exe"
                if ($installers) {
                    Write-Host "Archivos de instalacion creados:" -ForegroundColor Cyan
                    foreach ($installer in $installers) {
                        $sizeMB = [math]::Round($installer.Length/1MB, 2)
                        Write-Host "  - $($installer.Name) ($sizeMB MB)" -ForegroundColor White
                    }
                }
            }
        } else {
            Write-ErrorMsg "La compilacion del instalador fallo"
        }
    } else {
        Write-InfoMsg "Compilacion del instalador cancelada por el usuario"
    }
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Presione Enter para finalizar"

