# src/comparison/diff_generator.py

import pandas as pd
from src.utils.exceptions import DiffGenerationError
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def generate_diffs(current: pd.DataFrame, previous: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un DataFrame con las diferencias entre el mes actual y el mes anterior.
    
    Agrupa los datos por rut/nombre, suma los valores de debitos, creditos y saldo,
    y calcula las diferencias entre ambos períodos.
    
    Args:
        current: DataFrame del mes actual con columnas: rut, nombre, debitos, creditos, saldo
        previous: DataFrame del mes anterior con las mismas columnas
    
    Returns:
        pd.DataFrame: DataFrame con columnas: Nombre, Rut, diff_debito, diff_credito, diff_saldo
    
    Raises:
        DiffGenerationError: Si hay un error durante la generación de diferencias
    """
    logger.info("Generando diferencias intermensuales")

    try:
        # Validar que los DataFrames tengan las columnas necesarias
        required_columns = ['rut', 'nombre', 'debitos', 'creditos', 'saldo']
        for df_name, df in [('current', current), ('previous', previous)]:
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                raise DiffGenerationError(
                    f"El DataFrame {df_name} no tiene las columnas requeridas: {missing_cols}"
                )
        
        # Convertir columnas numéricas a float, manejando valores no numéricos
        numeric_columns = ['debitos', 'creditos', 'saldo']
        for col in numeric_columns:
            current[col] = pd.to_numeric(current[col], errors='coerce').fillna(0)
            previous[col] = pd.to_numeric(previous[col], errors='coerce').fillna(0)
        
        # Agrupar por rut y nombre, sumando los valores numéricos
        # Esto maneja casos donde un socio puede tener múltiples registros
        logger.debug("Agrupando datos del mes actual por rut/nombre")
        current_grouped = current.groupby(['rut', 'nombre']).agg({
            'debitos': 'sum',
            'creditos': 'sum',
            'saldo': 'sum'
        }).reset_index()
        
        logger.debug("Agrupando datos del mes anterior por rut/nombre")
        previous_grouped = previous.groupby(['rut', 'nombre']).agg({
            'debitos': 'sum',
            'creditos': 'sum',
            'saldo': 'sum'
        }).reset_index()
        
        # Hacer merge por rut y nombre usando outer join para incluir todos los registros
        # Esto permite detectar socios nuevos o que ya no están
        logger.debug("Realizando merge entre meses actual y anterior")
        merged = pd.merge(
            current_grouped,
            previous_grouped,
            on='nombre',
            how='outer',
            suffixes=('_current', '_previous')
        )
        
        # Rellenar valores NaN con 0 para el cálculo de diferencias
        for col in numeric_columns:
            merged[f'{col}_current'] = merged[f'{col}_current'].fillna(0)
            merged[f'{col}_previous'] = merged[f'{col}_previous'].fillna(0)
        
        # Calcular diferencias (mes actual - mes anterior)
        merged['diff_debito'] = merged['debitos_current'] - merged['debitos_previous']
        merged['diff_credito'] = merged['creditos_current'] - merged['creditos_previous']
        merged['diff_saldo'] = merged['saldo_current'] - merged['saldo_previous']

        merged['rut'] = merged['rut_current'].fillna(merged['rut_previous'])
        
        # Seleccionar y renombrar columnas según el formato requerido
        diffs = merged[[
            'nombre',
            'rut',
            'diff_debito',
            'diff_credito',
            'diff_saldo'
        ]].copy()
        
        # Renombrar columnas para que empiecen con mayúscula
        diffs.columns = ['Nombre', 'Rut', 'diff_debito', 'diff_credito', 'diff_saldo']
        
        # Ordenar por nombre para consistencia
        diffs = diffs.sort_values('Nombre').reset_index(drop=True)
        
    except DiffGenerationError:
        raise
    except Exception as e:
        logger.exception("Error generando diferencias")
        raise DiffGenerationError("No se pudieron generar las diferencias") from e

    logger.info(f"Diferencias generadas: {len(diffs)} filas")
    return diffs
