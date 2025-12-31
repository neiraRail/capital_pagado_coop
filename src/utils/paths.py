# src/utils/paths.py

from pathlib import Path

BASE_DATA = Path("data")
BASE_REPORTS = Path("reports")

def get_raw_xls_path(year, month):
    return BASE_DATA / "raw" / f"{year}-{month:02d}" / "original.xls"

def get_original_csv_path(year, month):
    return BASE_DATA / "original" / f"{year}-{month:02d}" / "original.csv"

def get_diff_csv_path(year, month):
    return BASE_DATA / "diffs" / f"{year}-{month:02d}" / "diffs.csv"

def get_processed_csv_path(year, month):
    return BASE_DATA / "processed" / f"{year}-{month:02d}" / "bueno.csv"

def get_report_paths(year, month):
    base = f"{year}-{month:02d}"
    return (
        BASE_REPORTS / "excel" / base / "reporte.xlsx",
        BASE_REPORTS / "word" / base / "reporte.docx",
    )