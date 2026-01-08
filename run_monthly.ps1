# Script PowerShell para ejecutar el proceso de capital pagado mensualmente
# Este script puede ser ejecutado manualmente o configurado en Windows Task Scheduler

# Cambiar al directorio del script
Set-Location $PSScriptRoot

# Activar el entorno virtual
& ".\env\Scripts\Activate.ps1"

# Ejecutar el script principal con modo automático (mes anterior)
python capital_pagado.py --auto

# Desactivar el entorno virtual
deactivate

