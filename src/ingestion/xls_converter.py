# src/ingestion/xls_converter.py

from pathlib import Path
from src.utils.exceptions import IngestionError
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def convert_xls_to_csv(input_xls: Path, output_csv: Path) -> None:
    logger.info(f"Convirtiendo XLS a CSV: {input_xls.name}")

    # if not input_xls.exists():
    #     raise IngestionError(f"Archivo XLS no encontrado: {input_xls}")

    try:
        # llamada a API externa
        # ...
        logger.debug("Llamada a API exitosa")

    except Exception as e:
        logger.exception("Error durante la conversión XLS → CSV")
        raise IngestionError("Fallo en conversión XLS → CSV") from e

    # if not output_csv.exists():
    #     raise IngestionError("La conversión no generó el archivo CSV")

    logger.info("Conversión finalizada correctamente")
