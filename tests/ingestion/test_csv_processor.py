# tests/ingestion/test_csv_processor.py

from pathlib import Path
import pytest
import pandas as pd

from src.ingestion.csv_processor import process_csv
from src.utils.exceptions import IngestionError


class TestCsvProcessor:
    """Tests para el componente de procesamiento de CSV."""

    @pytest.fixture
    def csv_path(self):
        """Ruta al archivo CSV de prueba."""
        return Path("data/original/202509.csv")

    @pytest.fixture
    def base_path(self):
        """Ruta al archivo base para regularización de nombres."""
        return Path("data/dictionary/base.csv")

    @pytest.fixture
    def diccionario_path(self):
        """Ruta al archivo diccionario de RUTs faltantes."""
        return Path("data/dictionary/ruts_faltantes.csv")

    def test_process_csv_reads_file_correctly(self, csv_path, base_path, diccionario_path):
        """
        Test que valida que el proceso lee correctamente el archivo CSV.
        
        Validación 1: Que el proceso lee correctamente el archivo csv.
        """
        # Ejecutar el procesamiento
        df = process_csv(
            csv_path=csv_path,
            base_path=base_path,
            diccionario_path=diccionario_path
        )
        
        # Validar que se generó un DataFrame
        assert isinstance(df, pd.DataFrame), "El resultado no es un DataFrame"
        
        # Validar que el DataFrame tiene las columnas esperadas
        expected_columns = ['rut', 'nombre_1', 'tipo', 'nombre_2', 'debitos', 'creditos', 'saldo', 'categoria', 'nombre']
        assert list(df.columns) == expected_columns, f"Las columnas no coinciden. Esperadas: {expected_columns}, Obtenidas: {list(df.columns)}"
        
        # Validar que el DataFrame no está vacío
        assert len(df) > 0, "El DataFrame está vacío"

    def test_process_csv_generates_expected_row_count_with_dictionary(self, csv_path, base_path, diccionario_path):
        """
        Test que valida que el proceso genera un DataFrame con 937 filas cuando se utiliza el diccionario.
        
        Validación 2: Que el proceso genera un dataframe con 937 filas si se utiliza el diccionario disponible.
        """
        # Ejecutar el procesamiento con diccionario
        df = process_csv(
            csv_path=csv_path,
            base_path=base_path,
            diccionario_path=diccionario_path
        )
        
        # Validar que tiene exactamente 937 filas
        assert len(df) == 937, f"El DataFrame tiene {len(df)} filas, se esperaban 937"
        
        # Validar que no hay nombres sin resolver
        nombres_sin_resolver = df[df["nombre"] == "No está"]
        assert len(nombres_sin_resolver) == 0, f"Se encontraron {len(nombres_sin_resolver)} nombres sin resolver"

    def test_process_csv_raises_error_without_dictionary(self, csv_path, base_path):
        """
        Test que valida que el proceso lanza un error si no se utiliza el diccionario.
        
        Validación 3: Que el proceso entrega un error si no se utiliza el diccionario 
        (ya que habrían ruts sin nombre). El archivo base se utilizaría siempre.
        """
        # Ejecutar el procesamiento sin diccionario (solo con base)
        with pytest.raises(IngestionError) as exc_info:
            process_csv(
                csv_path=csv_path,
                base_path=base_path,
                diccionario_path=None
            )
        
        # Validar que el error contiene información sobre los RUTs faltantes
        error_message = str(exc_info.value)
        assert "registros sin nombre resuelto" in error_message or "RUTs afectados" in error_message, \
            "El mensaje de error no contiene información sobre los RUTs faltantes"
        
        # Validar que el error menciona el diccionario
        assert "diccionario" in error_message.lower(), \
            "El mensaje de error debería mencionar el diccionario"

