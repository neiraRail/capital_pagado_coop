# src/consolidation/monthly_builder.py

import pandas as pd
from src.utils.exceptions import ConsolidationError
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def build_monthly_file(diffs: pd.DataFrame, previous_good: pd.DataFrame) -> pd.DataFrame:
    """
    Construye el archivo bueno del mes actual sumando las diferencias al archivo bueno del mes anterior.
    
    El proceso consiste en:
    1. Renombrar las columnas de diferencias (diff_debito, diff_credito, diff_saldo) 
       a (Debito, Credito, Saldo)
    2. Concatenar ambos dataframes
    3. Normalizar la columna Rut (convertir a mayúsculas y eliminar espacios en blanco)
    4. Agrupar por Rut y sumar las columnas numéricas
    5. Recuperar el Nombre y otras columnas necesarias del dataframe original
    
    Args:
        diffs: DataFrame con las diferencias. Debe tener columnas: Nombre, Rut, diff_debito, 
               diff_credito, diff_saldo
        previous_good: DataFrame del archivo bueno del mes anterior. Debe tener columnas: 
                      Rut, Debito, Credito, Saldo, Cuotas, Nombre
    
    Returns:
        pd.DataFrame: DataFrame consolidado con columnas: Rut, Debito, Credito, Saldo, Cuotas, Nombre
    
    Raises:
        ConsolidationError: Si hay un error durante la consolidación
    """
    logger.info("Construyendo archivo Bueno del mes")

    try:
        # Validar columnas requeridas en diffs
        required_diff_cols = ['Nombre', 'Rut', 'diff_debito', 'diff_credito', 'diff_saldo']
        missing_diff_cols = [col for col in required_diff_cols if col not in diffs.columns]
        if missing_diff_cols:
            raise ConsolidationError(
                f"El DataFrame de diferencias no tiene las columnas requeridas: {missing_diff_cols}"
            )
        
        # Validar columnas requeridas en previous_good
        required_prev_cols = ['Rut', 'Debito', 'Credito', 'Saldo', 'Nombre']
        missing_prev_cols = [col for col in required_prev_cols if col not in previous_good.columns]
        if missing_prev_cols:
            raise ConsolidationError(
                f"El DataFrame previous_good no tiene las columnas requeridas: {missing_prev_cols}"
            )
        
        # Crear una copia del dataframe de diferencias y renombrar columnas
        # según el proceso antiguo: diff_debito -> Debito, diff_credito -> Credito, diff_saldo -> Saldo
        diffs_renamed = diffs.copy()
        diffs_renamed = diffs_renamed.rename(columns={
            'diff_debito': 'Debito',
            'diff_credito': 'Credito',
            'diff_saldo': 'Saldo'
        })
        
        # Seleccionar solo las columnas necesarias para la concatenación
        diffs_for_merge = diffs_renamed[['Rut', 'Debito', 'Credito', 'Saldo', 'Nombre']].copy()
        previous_for_merge = previous_good[['Rut', 'Debito', 'Credito', 'Saldo', 'Nombre']].copy()
        
        # Si previous_good tiene Cuotas, preservarla temporalmente para el merge
        has_cuotas = 'Cuotas' in previous_good.columns
        if has_cuotas:
            previous_for_merge['Cuotas'] = previous_good['Cuotas']
        
        # Concatenar ambos dataframes (proceso antiguo: pd.concat([anteriorBueno, dif]))
        logger.debug("Concatenando dataframes de diferencias y archivo bueno anterior")
        concatenated = pd.concat([previous_for_merge, diffs_for_merge], ignore_index=True)
        
        # Normalizar la columna Rut antes del groupby:
        # 1. Convertir a mayúsculas (para manejar 'k' y 'K')
        # 2. Eliminar espacios en blanco antes y después
        logger.debug("Normalizando columna Rut: convirtiendo a mayúsculas y eliminando espacios")
        concatenated['Rut'] = concatenated['Rut'].astype(str).str.upper().str.strip()
        
        # Agrupar por Rut y sumar las columnas numéricas
        # El proceso antiguo: .groupby(['Rut']).sum().reset_index()
        logger.debug("Agrupando por Rut y sumando columnas numéricas")
        # Especificar numeric_only=True para evitar problemas con columnas de texto
        numeric_cols = ['Debito', 'Credito', 'Saldo']
        if has_cuotas:
            numeric_cols.append('Cuotas')
        
        grouped = concatenated.groupby('Rut', as_index=False)[numeric_cols].sum()
        
        # Recuperar el Nombre haciendo merge con el dataframe concatenado original
        # El proceso antiguo: pd.merge(merged_df, pd.concat([anteriorBueno, dif])[["Rut", "Nombre"]], on='Rut')
        logger.debug("Recuperando información de Nombre mediante merge")
        name_df = concatenated[['Rut', 'Nombre']].drop_duplicates(subset=['Rut'], keep='first')
        result = pd.merge(grouped, name_df, on='Rut', how='left')
        
        # Eliminar duplicados por Rut (proceso antiguo: drop_duplicates(subset=['Rut'], keep='first'))
        result = result.drop_duplicates(subset=['Rut'], keep='first')
        
        # Eliminar filas con Saldo = 0 (según el proceso antiguo)
        result = result[(result['Saldo'] != 0) & (result['Saldo'].notna())]
        
        # Recalcular Cuotas basándose en Saldo (según el proceso antiguo: capital['Cuotas'] = capital['Saldo'].apply(lambda x: x//1000))
        if has_cuotas:
            result['Cuotas'] = (result['Saldo'] / 1000).astype(int)
        else:
            # Si no tenía Cuotas, calcularlas basándose en Saldo
            result['Cuotas'] = (result['Saldo'] / 1000).astype(int)
        
        # Reordenar columnas según el formato esperado: Rut, Debito, Credito, Saldo, Cuotas, Nombre
        result = result[['Rut', 'Debito', 'Credito', 'Saldo', 'Cuotas', 'Nombre']]
        
        # Resetear índice
        result = result.reset_index(drop=True)
        
    except ConsolidationError:
        raise
    except Exception as e:
        logger.exception("Error en consolidación mensual")
        raise ConsolidationError("Fallo al construir archivo mensual") from e

    logger.info(f"Archivo mensual generado: {len(result)} registros")
    return result
