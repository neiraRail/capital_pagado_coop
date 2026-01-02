# tests/ingestion/test_xls_converter.py

import csv
from pathlib import Path
import pytest

from src.ingestion.xls_converter import convert_xls_to_csv


class TestXlsConverter:
    """Tests para el componente de conversión XLS a CSV."""

    @pytest.fixture
    def input_xls_path(self):
        """Ruta al archivo XLS de prueba."""
        return Path("data/raw/202509.xls")

    @pytest.fixture
    def output_csv_path(self, tmp_path):
        """Ruta temporal para el archivo CSV de salida."""
        return tmp_path / "output_test.csv"

    def test_conversion_generates_csv_file(self, input_xls_path, output_csv_path):
        """
        Test que valida que la conversión genera un archivo CSV.
        
        Validación 1: Que se genera un archivo csv.
        """
        # Ejecutar la conversión
        convert_xls_to_csv(input_xls_path, output_csv_path)
        
        # Validar que el archivo CSV fue generado
        assert output_csv_path.exists(), "El archivo CSV no fue generado"
        assert output_csv_path.is_file(), "La ruta generada no es un archivo"

    def test_csv_has_expected_row_count(self, input_xls_path, output_csv_path):
        """
        Test que valida que el CSV generado tiene exactamente 9285 filas.
        
        Validación 2: Que el csv que se genera contiene 9285 filas.
        """
        # Ejecutar la conversión
        convert_xls_to_csv(input_xls_path, output_csv_path)
        
        # Validar que el archivo existe
        assert output_csv_path.exists(), "El archivo CSV no fue generado"
        
        # Contar las filas del CSV (incluyendo el header)
        with open(output_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            row_count = sum(1 for _ in reader)
        
        # Validar que tiene exactamente 9285 filas
        assert row_count == 9285, f"El CSV tiene {row_count} filas, se esperaban 9285"

