# src/reporting/excel_report.py

import pandas as pd
from pathlib import Path
from src.utils.exceptions import ReportingError
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def generate_excel_report(df: pd.DataFrame, output_path: Path):
    """
    Genera un reporte Excel con las columnas: Nombre, Rut, Saldo, Cuotas.
    
    Args:
        df: DataFrame con columnas: Rut, Debito, Credito, Saldo, Cuotas, Nombre
        output_path: Ruta donde se guardará el archivo Excel
    """
    logger.info(f"Generando reporte Excel: {output_path.name}")
    
    try:
        # Asegurar que el directorio existe
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Validar que el DataFrame tiene las columnas necesarias
        required_cols = ['Nombre', 'Rut', 'Saldo', 'Cuotas']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ReportingError(
                f"El DataFrame no tiene las columnas requeridas: {missing_cols}"
            )
        
        # Seleccionar y reordenar columnas según el formato esperado
        report_df = df[['Nombre', 'Rut', 'Saldo', 'Cuotas']].copy()
        
        # Guardar a Excel sin índice
        report_df.to_excel(output_path, index=False)
        
        logger.info(f"Reporte Excel generado exitosamente: {output_path}")
        
    except ReportingError:
        raise
    except Exception as e:
        logger.exception("Error generando reporte Excel")
        raise ReportingError("No se pudo generar el reporte Excel") from e