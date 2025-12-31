# src/reporting/word_report.py

from docx import Document
from pathlib import Path
from src.utils.exceptions import ReportingError
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def generate_word_report(df, output_path: Path):
    logger.info(f"Generando reporte Word: {output_path.name}")

    try:
        # doc = Document()
        # doc.save(output_path)
        pass
    except Exception as e:
        logger.exception("Error generando reporte Word")
        raise ReportingError("No se pudo generar el reporte Word") from e
