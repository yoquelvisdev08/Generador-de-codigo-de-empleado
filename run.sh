#!/bin/bash
# Script para ejecutar la aplicación usando el entorno virtual

# Activar el entorno virtual
source "$(dirname "$0")/env/bin/activate"

# Ejecutar la aplicación
python3 main.py

