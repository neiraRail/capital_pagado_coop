# Instrucciones para Ejecución Mensual del Proceso de Capital Pagado

Este documento explica cómo ejecutar el proceso de capital pagado mensualmente de forma automatizada.

## Opciones de Ejecución

### 1. Ejecución Manual

#### Opción A: Usar el script batch (recomendado en Windows)
```bash
run_monthly.bat
```

#### Opción B: Usar el script PowerShell
```powershell
.\run_monthly.ps1
```

#### Opción C: Ejecutar directamente con Python
```bash
python capital_pagado.py --auto
```

#### Opción D: Ejecutar para un período específico
```bash
python capital_pagado.py --year 2025 --month 9
```

### 2. Ejecución Automatizada con Windows Task Scheduler

Para automatizar la ejecución mensual usando el Programador de tareas de Windows:

#### Paso 1: Abrir el Programador de tareas
1. Presiona `Win + R`
2. Escribe `taskschd.msc` y presiona Enter
3. O busca "Programador de tareas" en el menú de inicio

#### Paso 2: Crear una nueva tarea
1. En el panel derecho, haz clic en "Crear tarea básica..." o "Crear tarea..."
2. **Nombre**: "Proceso Capital Pagado Mensual"
3. **Descripción**: "Ejecuta el proceso de capital pagado para el mes anterior"

#### Paso 3: Configurar el desencadenador (Trigger)
1. Ve a la pestaña **"Desencadenadores"**
2. Haz clic en **"Nuevo"**
3. Configura:
   - **Iniciar la tarea**: "En una programación"
   - **Configuración**: "Mensual"
   - **Día**: Selecciona el día del mes (recomendado: día 2 o 3 para asegurar que los datos del mes anterior estén disponibles)
   - **Mes**: Todos los meses (o selecciona los meses específicos)
   - **A las**: Selecciona la hora (ej: 09:00)
   - **Repetir cada**: 1 mes
4. Haz clic en **"Aceptar"**

#### Paso 4: Configurar la acción (Action)
1. Ve a la pestaña **"Acciones"**
2. Haz clic en **"Nueva"**
3. Configura:
   - **Acción**: "Iniciar un programa"
   - **Programa o script**: Ruta completa a `run_monthly.bat`
     - Ejemplo: `C:\Users\neira\Desktop\kumemogen\CapitalPagado4.0\capital_pagado_coop\run_monthly.bat`
   - **Iniciar en**: Ruta del directorio del proyecto
     - Ejemplo: `C:\Users\neira\Desktop\kumemogen\CapitalPagado4.0\capital_pagado_coop`
4. Haz clic en **"Aceptar"**

#### Paso 5: Configurar condiciones (opcional)
1. Ve a la pestaña **"Condiciones"**
2. Asegúrate de que:
   - ✓ "Iniciar la tarea solo si el equipo está conectado a la alimentación de CA" esté desmarcado (si quieres que se ejecute en laptops)
   - ✓ "Activar la tarea solo si el equipo está conectado a la red" esté desmarcado (si no necesitas red)
   - ✓ "Activar el equipo para ejecutar esta tarea" esté marcado (para que la computadora se active si está en modo suspendido)

#### Paso 6: Configurar configuración (opcional)
1. Ve a la pestaña **"Configuración"**
2. Asegúrate de que:
   - "Permitir la ejecución de la tarea a petición" esté marcado
   - "Ejecutar la tarea lo antes posible después de que se pierda una programación programada" esté marcado
   - "Si la tarea ya se está ejecutando, aplicar la siguiente regla" esté configurado como "No iniciar una nueva instancia"

#### Paso 7: Configurar la seguridad
1. Ve a la pestaña **"General"**
2. Asegúrate de que:
   - "Ejecutar tanto si el usuario ha iniciado sesión como si no" esté seleccionado
   - O "Ejecutar solo cuando el usuario haya iniciado sesión" si prefieres
   - Marca "Ejecutar con los privilegios más altos" si es necesario
   - Haz clic en "Cambiar usuario o grupo" y selecciona tu usuario o SYSTEM

#### Paso 8: Guardar y probar
1. Haz clic en **"Aceptar"**
2. Ingresa tu contraseña si es necesario
3. Para probar, haz clic derecho en la tarea y selecciona **"Ejecutar"**

## Verificación de Logs

Los logs se generan automáticamente en la carpeta `logs/` con nombres como:
- `run_YYYYMMDD_HHMMSS.log`

Revisa estos logs para verificar que el proceso se ejecutó correctamente.

## Notas Importantes

1. **Archivo XLS requerido**: Asegúrate de que el archivo XLS del mes a procesar esté disponible en la carpeta `data/raw/` con el formato `YYYYMM.xls` antes de ejecutar el proceso.

2. **Dependencias**: El proceso requiere que el archivo procesado del mes anterior exista en `data/processed/` para generar las diferencias.

3. **Ejecución del mes anterior**: El modo `--auto` ejecuta automáticamente para el mes anterior al actual. Por ejemplo:
   - Si ejecutas en febrero 2025, procesará enero 2025
   - Si ejecutas en enero 2025, procesará diciembre 2024

4. **Programación recomendada**: Programa la tarea para el día 2 o 3 de cada mes, para asegurar que los datos del mes anterior estén disponibles.

## Troubleshooting

### La tarea no se ejecuta
- Verifica que la ruta al script sea correcta
- Verifica que el entorno virtual esté configurado correctamente
- Revisa los logs de Windows Event Viewer (Registro de eventos de Windows)
- Ejecuta manualmente el script para verificar que funciona

### Error de permisos
- Asegúrate de tener permisos para ejecutar scripts
- En PowerShell, puede ser necesario ejecutar: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Error de Python no encontrado
- Verifica que Python esté en el PATH del sistema
- O modifica los scripts para usar la ruta completa al Python del entorno virtual:
  - `env\Scripts\python.exe capital_pagado.py --auto`

