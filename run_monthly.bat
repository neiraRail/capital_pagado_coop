@echo off
REM Script para ejecutar el proceso de capital pagado mensualmente
REM Este script puede ser ejecutado manualmente o configurado en Windows Task Scheduler

REM Cambiar al directorio del proyecto
cd /d "%~dp0"

REM Activar el entorno virtual
call env\Scripts\activate.bat

REM Ejecutar el script principal con modo automático (mes anterior)
python capital_pagado.py --auto

REM Desactivar el entorno virtual
call env\Scripts\deactivate.bat

