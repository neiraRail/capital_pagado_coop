# src/reporting/word_report.py

from docx import Document
from pathlib import Path
from src.utils.exceptions import ReportingError
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

def generate_excel_report(df, output_path: Path):
    logger.info(f"Generando reporte Excel: {output_path.name}")
    try:
        # Lógica para generar el reporte Excel
        pass
    except Exception as e:
        logger.exception("Error generando reporte Excel")
        raise ReportingError("No se pudo generar el reporte Excel") from e