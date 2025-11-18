# -*- mode: python ; coding: utf-8 -*-
"""
Archivo de especificación de PyInstaller para el Generador de Códigos de Carnet
Este archivo define cómo se debe compilar la aplicación en un ejecutable único
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Nombre de la aplicación
APP_NAME = 'GeneradorCodigosCarnet'

# Recopilar todos los submódulos necesarios
hiddenimports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtWebEngineCore',
    'PyQt6.QtWebChannel',
    'PyQt6.QtPrintSupport',
    'barcode',
    'barcode.writer',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'openpyxl',
    'openpyxl.cell',
    'openpyxl.styles',
    'numpy',
    'pyzbar',
    'pyzbar.pyzbar',
    'sqlite3',
    'dotenv',
    'logging',
    'hashlib',
    'secrets',
    'json',
    'csv',
    'datetime',
    'pathlib',
]

# Recopilar archivos de datos de los paquetes
datas = []
datas += collect_data_files('PyQt6')
datas += collect_data_files('barcode')
datas += collect_data_files('pyzbar')

# Agregar los directorios de la aplicación
datas += [
    ('../assets', 'assets'),
    ('../data/templates_carnet', 'data/templates_carnet'),
    ('../config', 'config'),
    ('../src', 'src'),
]

# Obtener ruta base del proyecto de forma robusta
# El archivo .spec está en installer/, así que subimos un nivel
SPEC_FILE_PATH = os.path.abspath(SPEC)
INSTALLER_DIR = os.path.dirname(SPEC_FILE_PATH)
PROJECT_ROOT = os.path.dirname(INSTALLER_DIR)  # Subir desde installer/ al root
ICON_PATH = os.path.join(PROJECT_ROOT, 'assets', 'logo.ico')

print(f"[DEBUG] SPEC file: {SPEC_FILE_PATH}")
print(f"[DEBUG] Installer dir: {INSTALLER_DIR}")
print(f"[INFO] Directorio del proyecto: {PROJECT_ROOT}")
print(f"[INFO] Ruta del icono: {ICON_PATH}")
print(f"[INFO] Icono existe: {os.path.exists(ICON_PATH)}")
if os.path.exists(ICON_PATH):
    icon_size = os.path.getsize(ICON_PATH)
    print(f"[INFO] Tamaño del icono: {icon_size:,} bytes ({icon_size/1024:.2f} KB)")

# Análisis de archivos Python
a = Analysis(
    ['../main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'tkinter',
        '_tkinter',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Eliminar archivos innecesarios para reducir el tamaño
exclude_binaries = [
    'opengl32sw.dll',  # OpenGL software renderer (muy grande y no necesario)
    'Qt6Pdf.dll',
    'Qt6VirtualKeyboard.dll',
]

a.binaries = [x for x in a.binaries if not any(excl in x[0] for excl in exclude_binaries)]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No mostrar consola en Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH if os.path.exists(ICON_PATH) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

