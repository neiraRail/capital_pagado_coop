# src/consolidation/monthly_builder.py

import pandas as pd
from src.utils.exceptions import ConsolidationError
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def build_monthly_file(diffs: pd.DataFrame, previous_good: pd.DataFrame) -> pd.DataFrame:
    logger.info("Construyendo archivo Bueno del mes")

    try:
        result = pd.DataFrame()  # Placeholder para la lógica real de consolidación
    except Exception as e:
        logger.exception("Error en consolidación mensual")
        raise ConsolidationError("Fallo al construir archivo mensual") from e

    logger.info(f"Archivo mensual generado: {len(result)} registros")
    return result
