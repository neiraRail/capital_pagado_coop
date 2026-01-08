from pathlib import Path
import pandas as pd
import argparse
from datetime import datetime, timedelta

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



def get_last_month():
    """Obtiene el año y mes del período anterior al actual."""
    today = datetime.now()
    # Obtener el primer día del mes actual y restar un día para obtener el último día del mes anterior
    first_day_current = today.replace(day=1)
    last_day_previous = first_day_current - timedelta(days=1)
    return last_day_previous.year, last_day_previous.month


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Procesa los datos de capital pagado para un período mensual específico."
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Año a procesar (formato: YYYY). Si no se especifica, se usa el mes anterior.",
    )
    parser.add_argument(
        "--month",
        type=int,
        help="Mes a procesar (1-12). Si no se especifica, se usa el mes anterior.",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Ejecutar automáticamente para el mes anterior sin requerir argumentos.",
    )

    args = parser.parse_args()

    # Si se usa --auto o no se proporcionan argumentos, usar el mes anterior
    if args.auto or (args.year is None and args.month is None):
        year, month = get_last_month()
        logger.info(f"Ejecutando automáticamente para el mes anterior: {year}-{month:02d}")
    elif args.year is not None and args.month is not None:
        year = args.year
        month = args.month
        logger.info(f"Ejecutando para el período especificado: {year}-{month:02d}")
    else:
        parser.error("Debe proporcionar ambos --year y --month, o usar --auto para el mes anterior.")

    # Validar mes
    if not (1 <= month <= 12):
        parser.error(f"El mes debe estar entre 1 y 12. Se recibió: {month}")

    # Validar año razonable
    current_year = datetime.now().year
    if year < 2000 or year > current_year + 1:
        parser.error(f"El año debe estar entre 2000 y {current_year + 1}. Se recibió: {year}")

    try:
        run_month(year=year, month=month)
    except Exception as e:
        logger.error(f"Error durante la ejecución: {e}")
        exit(1)