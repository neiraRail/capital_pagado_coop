from pathlib import Path
import pandas as pd

from src.ingestion.xls_converter import convert_xls_to_csv
from src.ingestion.csv_processor import process_csv
from src.comparison.diff_generator import generate_diffs
from src.consolidation.monthly_builder import build_monthly_file
from src.reporting.excel_report import generate_excel_report
from src.reporting.word_report import generate_word_report
from src.utils.paths import (
    get_raw_xls_path,
    get_original_csv_path,
    get_diff_csv_path,
    get_processed_csv_path,
    get_report_paths,
    get_base_path,
    get_dictionary_path,
)
from src.utils.dates import get_previous_period
from src.utils.logging import setup_logger
from src.utils.exceptions import PipelineError

logger = setup_logger(__name__)


def run_month(year: int, month: int):
    try:
        logger.info(f"Procesando período {year}-{month:02d}")

        prev_year, prev_month = get_previous_period(year, month)

        # 1. Conversión XLS → CSV
        raw_xls = get_raw_xls_path(year, month)
        original_csv = get_original_csv_path(year, month)
        logger.info(f"Convirtiendo {raw_xls.parent.name + '/' + raw_xls.name} a {original_csv.parent.name + '/' + original_csv.name}")

        convert_xls_to_csv(raw_xls, original_csv)

        # 2. Procesamiento de datos CSV
        base_path = get_base_path()
        diccionario_path = get_dictionary_path()
        
        logger.info(f"Procesando CSV del mes actual: {original_csv.name}")
        df_current = process_csv(
            original_csv,
            base_path=base_path,
            diccionario_path=diccionario_path
        )
        
        previous_csv = get_original_csv_path(prev_year, prev_month)
        logger.info(f"Procesando CSV del mes anterior: {previous_csv.name}")
        df_previous = process_csv(
            previous_csv,
            base_path=base_path,
            diccionario_path=diccionario_path
        )

        # 3. Generación de diferencias
        df_diffs = generate_diffs(df_current, df_previous)
        diffs_path = get_diff_csv_path(year, month)
        df_diffs.to_csv(diffs_path, index=False)

        # 4. Consolidación mensual
        df_previous_good = pd.read_csv(
            get_processed_csv_path(prev_year, prev_month)
        )

        df_good = build_monthly_file(df_diffs, df_previous_good)
        processed_path = get_processed_csv_path(year, month)
        df_good.to_csv(processed_path, index=False)

        # 5. Reportes
        excel_path, word_path = get_report_paths(year, month)

        generate_excel_report(df_good, excel_path)
        generate_word_report(df_good, word_path)

        logger.info("Proceso finalizado correctamente")
    except PipelineError as e:
        logger.error(f"Fallo en el pipeline: {e}")
        raise
    except Exception as e:
        logger.exception("Error inesperado en el pipeline")
        raise



if __name__ == "__main__":
    # ejecución manual
    run_month(year=2025, month=9)