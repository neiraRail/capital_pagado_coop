# src/comparison/diff_generator.py

import pandas as pd
from src.utils.exceptions import DiffGenerationError
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def generate_diffs(current: pd.DataFrame, previous: pd.DataFrame) -> pd.DataFrame:
    logger.info("Generando diferencias intermensuales")

    try:
        # tu lógica existente
        diffs = pd.DataFrame()  # Placeholder para la lógica real de diferencias
    except Exception as e:
        logger.exception("Error generando diferencias")
        raise DiffGenerationError("No se pudieron generar las diferencias") from e

    logger.info(f"Diferencias generadas: {len(diffs)} filas")
    return diffs
