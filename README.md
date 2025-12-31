# capital_pagado_coop
Repo para proyecto de generación de informes de capital pagado para la cooperativa Kume Mogen

## Contexto

El contexto de este repositorio es el siguiente:

Existe un archivo Excel mensual generado por un sistema contable legado. A partir de ese Excel se generan varios informes con:
- limpieza / depuración de datos,
- transformaciones,
- reglas de negocio ya definidas.

Toda la lógica ya existe, pero:
- está dispersa en notebooks Jupyter exploratorios,
- con código poco estructurado, difícil de mantener y reutilizar.

El objetivo ahora es:
- sistematizar y ordenar el código,
- diseñar una arquitectura de software clara y robusta,
- con calidad de código, separación de responsabilidades,
- que permita modificar reglas, cambiar partes o agregar nuevos informes en el futuro sin rehacer todo.

El sistema hoy es, conceptualmente, funciona de la siguiente manera:

```
XLS mensual
   ↓ (API externa)
CSV “Original” mes actual
   ↓
[ Comparación ]
CSV Diffs (mes-1 vs mes)
   ↓
[ Consolidación ]
CSV “Bueno” mes actual
   ↓
[ Reporting ]
Excel informe + Word informe
   ↓
[ Envío manual por mail ]
```

Puntos clave:
- Hay dependencia temporal (mes actual ↔ mes anterior).
- Existen artefactos intermedios (CSVs auxiliares) que son importantes y no deben desaparecer.
- La lógica está bien definida, solo mal empaquetada.

Se define una arquitectura de  aplicación Python modular tipo “data pipeline” y se van a aplicar los siguientes principios:

✔ Separación por responsabilidades
- Ingestión
- Transformación
- Reglas
- Reporting
- Orquestación

✔ Código “replaceable”
- El conversor XLS→CSV debe ser intercambiable
- El output Word / Excel debe poder cambiar sin tocar el core

✔ Artefactos explícitos
- Los CSV intermedios siguen existiendo
- No todo vive solo en memoria

✔ Configuración externa
- Mes, año, rutas, nombres → config
- Nada hardcodeado en la lógica