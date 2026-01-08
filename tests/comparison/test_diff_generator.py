# tests/comparison/test_diff_generator.py

from pathlib import Path
import pytest
import pandas as pd

from src.ingestion.xls_converter import convert_xls_to_csv
from src.ingestion.csv_processor import process_csv
from src.comparison.diff_generator import generate_diffs


class TestDiffGenerator:
    """Tests para el componente de generación de diferencias intermensuales."""

    @pytest.fixture
    def original_csv_september(self, tmp_path):
        """Ruta al archivo CSV de septiembre (generado o existente)."""
        original_path = Path("data/original/202509.csv")
        if original_path.exists():
            return original_path
        # Si no existe, generar desde XLS
        output_path = tmp_path / "202509.csv"
        convert_xls_to_csv(Path("data/raw/202509.xls"), output_path)
        return output_path

    @pytest.fixture
    def original_csv_august(self, tmp_path):
        """Ruta al archivo CSV de agosto (generado o existente)."""
        original_path = Path("data/original/202508.csv")
        if original_path.exists():
            return original_path
        # Si no existe, generar desde XLS
        output_path = tmp_path / "202508.csv"
        convert_xls_to_csv(Path("data/raw/202508.xls"), output_path)
        return output_path

    @pytest.fixture
    def base_path(self):
        """Ruta al archivo base para regularización de nombres."""
        return Path("data/dictionary/base.csv")

    @pytest.fixture
    def diccionario_path(self):
        """Ruta al archivo diccionario de RUTs faltantes."""
        return Path("data/dictionary/ruts_faltantes.csv")

    @pytest.fixture
    def df_current(self, original_csv_september, base_path, diccionario_path):
        """DataFrame procesado del mes actual (septiembre)."""
        return process_csv(
            csv_path=original_csv_september,
            base_path=base_path,
            diccionario_path=diccionario_path
        )

    @pytest.fixture
    def df_previous(self, original_csv_august, base_path, diccionario_path):
        """DataFrame procesado del mes anterior (agosto)."""
        return process_csv(
            csv_path=original_csv_august,
            base_path=base_path,
            diccionario_path=diccionario_path
        )

    def test_generate_diffs_returns_dataframe(self, df_current, df_previous):
        """
        Test que valida que generate_diffs retorna un DataFrame.
        
        Validación básica: Que la función retorna un DataFrame válido.
        """
        # Ejecutar la generación de diferencias
        diffs = generate_diffs(df_current, df_previous)
        
        # Validar que se generó un DataFrame
        assert isinstance(diffs, pd.DataFrame), "El resultado no es un DataFrame"
        
        # Validar que el DataFrame no está vacío
        assert len(diffs) > 0, "El DataFrame de diferencias está vacío"

    def test_generate_diffs_has_expected_columns(self, df_current, df_previous):
        """
        Test que valida que el DataFrame de diferencias tiene las columnas esperadas.
        
        Validación de estructura: Que el DataFrame tiene las columnas correctas.
        """
        # Ejecutar la generación de diferencias
        diffs = generate_diffs(df_current, df_previous)
        
        # Validar columnas esperadas
        expected_columns = ['Nombre', 'Rut', 'diff_debito', 'diff_credito', 'diff_saldo']
        assert list(diffs.columns) == expected_columns, \
            f"Las columnas no coinciden. Esperadas: {expected_columns}, Obtenidas: {list(diffs.columns)}"

    def test_generate_diffs_has_expected_row_count(self, df_current, df_previous):
        """
        Test que valida que el DataFrame de diferencias tiene exactamente 919 filas.
        
        Validación 1: Que el DataFrame generado tiene 919 filas.
        """
        # Ejecutar la generación de diferencias
        diffs = generate_diffs(df_current, df_previous)
        
        # Validar que tiene exactamente 908 filas
        assert len(diffs) == 919, \
            f"El DataFrame tiene {len(diffs)} filas, se esperaban 919"

    def test_generate_diffs_sum_diff_saldo_is_correct(self, df_current, df_previous):
        """
        Test que valida que la suma de diff_saldo es 717805.
        
        Validación 2: Que la suma de la columna diff_saldo para todo el DataFrame es 717805.
        """
        # Ejecutar la generación de diferencias
        diffs = generate_diffs(df_current, df_previous)
        
        # Calcular la suma de diff_saldo
        sum_diff_saldo = diffs['diff_saldo'].sum()
        
        # Validar que la suma es exactamente 717805
        assert sum_diff_saldo == 717805, \
            f"La suma de diff_saldo es {sum_diff_saldo}, se esperaba 717805"

