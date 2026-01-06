# src/utils/paths.py

from pathlib import Path

BASE_DATA = Path("data")
BASE_REPORTS = Path("reports")

def get_raw_xls_path(year, month):
    return BASE_DATA / "raw" / f"{year}{month:02d}.xls"

def get_original_csv_path(year, month):
    return BASE_DATA / "original" / f"{year}{month:02d}.csv"

def get_diff_csv_path(year, month):
    return BASE_DATA / "diffs" / f"{year}{month:02d}.csv"

def get_processed_csv_path(year, month):
    return BASE_DATA / "processed" / f"{year}{month:02d}.csv"

def get_report_paths(year, month):
    base = f"{year}{month:02d}"
    return (
        BASE_REPORTS / "excel" / base + "reporte.xlsx",
        BASE_REPORTS / "word" / base + "reporte.docx",
    )

def get_base_path():
    """
    Obtiene la ruta al archivo base para regularización de nombres.
    Este archivo se encuentra en data/dictionary/base.csv.
    """
    return BASE_DATA / "dictionary" / "base.csv"

def get_dictionary_path():
    """
    Obtiene la ruta al archivo diccionario de RUTs faltantes para regularización de nombres.
    """
    return BASE_DATA / "dictionary" / "ruts_faltantes.csv"