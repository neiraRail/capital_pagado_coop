# tests/consolidation/test_monthly_builder.py

from pathlib import Path
import pytest
import pandas as pd

from src.consolidation.monthly_builder import build_monthly_file


class TestMonthlyBuilder:
    """Tests para el componente de consolidación mensual."""

    @pytest.fixture
    def diff_csv(self):
        """Ruta al archivo CSV de diferencias de septiembre."""
        diff_path = Path("data/diffs/202509.csv")
        if not diff_path.exists():
            pytest.skip(f"Archivo de diferencias no encontrado: {diff_path}")
        return diff_path

    @pytest.fixture
    def previous_good_csv(self):
        """Ruta al archivo CSV procesado (bueno) de agosto."""
        processed_path = Path("data/processed/202508.csv")
        if not processed_path.exists():
            pytest.skip(f"Archivo procesado anterior no encontrado: {processed_path}")
        return processed_path

    @pytest.fixture
    def df_diffs(self, diff_csv):
        """DataFrame con las diferencias."""
        return pd.read_csv(diff_csv)

    @pytest.fixture
    def df_previous_good(self, previous_good_csv):
        """DataFrame del archivo bueno del mes anterior."""
        return pd.read_csv(previous_good_csv)

    def test_build_monthly_file_returns_dataframe(self, df_diffs, df_previous_good):
        """
        Test que valida que build_monthly_file retorna un DataFrame.
        
        Validación básica: Que la función retorna un DataFrame válido.
        """
        # Ejecutar la consolidación
        result = build_monthly_file(df_diffs, df_previous_good)
        
        # Validar que se generó un DataFrame
        assert isinstance(result, pd.DataFrame), "El resultado no es un DataFrame"
        
        # Validar que el DataFrame no está vacío
        assert len(result) > 0, "El DataFrame consolidado está vacío"

    def test_build_monthly_file_has_expected_columns(self, df_diffs, df_previous_good):
        """
        Test que valida que el DataFrame consolidado tiene las columnas esperadas.
        
        Validación de estructura: Que el DataFrame tiene las columnas correctas.
        """
        # Ejecutar la consolidación
        result = build_monthly_file(df_diffs, df_previous_good)
        
        # Validar columnas esperadas
        expected_columns = ['Rut', 'Debito', 'Credito', 'Saldo', 'Cuotas', 'Nombre']
        assert list(result.columns) == expected_columns, \
            f"Las columnas no coinciden. Esperadas: {expected_columns}, Obtenidas: {list(result.columns)}"

    def test_build_monthly_file_has_expected_row_count(self, df_diffs, df_previous_good):
        """
        Test que valida que el DataFrame consolidado tiene exactamente 932 filas.
        
        Validación 1: Que el DataFrame generado tiene 932 filas.
        """
        # Ejecutar la consolidación
        result = build_monthly_file(df_diffs, df_previous_good)
        
        # Validar que tiene exactamente 932 filas
        assert len(result) == 932, \
            f"El DataFrame tiene {len(result)} filas, se esperaban 932"

    def test_build_monthly_file_sum_saldo_is_correct(self, df_diffs, df_previous_good):
        """
        Test que valida que la suma de la columna Saldo es 177169221.
        
        Validación 2: Que la suma de la columna Saldo para todo el DataFrame es 177169221.
        """
        # Ejecutar la consolidación
        result = build_monthly_file(df_diffs, df_previous_good)
        
        # Calcular la suma de Saldo
        sum_saldo = result['Saldo'].sum()
        
        # Validar que la suma es exactamente 177169221
        assert sum_saldo == 177169221, \
            f"La suma de Saldo es {sum_saldo}, se esperaba 177169221"

