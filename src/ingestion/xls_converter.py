# src/ingestion/xls_converter.py

import os
import time
import base64
import requests
from pathlib import Path
from src.utils.exceptions import IngestionError
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

# API Key de Convertio (puede ser configurada mediante variable de entorno)
CONVERTIO_API_KEY = os.getenv("CONVERTIO_API_KEY", "2dae5621f2bcfb385f1db1f916b63223")
CONVERTIO_BASE_URL = "https://api.convertio.co/convert"


def convert_xls_to_csv(input_xls: Path, output_csv: Path) -> None:
    logger.info(f"Convirtiendo XLS a CSV: {input_xls.name}")

    if not input_xls.exists():
        raise IngestionError(f"Archivo XLS no encontrado: {input_xls}")

    try:
        # Asegurar que el directorio de salida exista
        output_csv.parent.mkdir(parents=True, exist_ok=True)

        # 1) Leer archivo y codificar a base64
        logger.debug(f"Leyendo archivo: {input_xls}")
        with open(input_xls, "rb") as f:
            file_bytes = f.read()

        file_b64 = base64.b64encode(file_bytes).decode("ascii")
        logger.debug(f"Archivo codificado en base64 ({len(file_b64)} caracteres)")

        # 2) Crear conversión con input = base64
        payload = {
            "apikey": CONVERTIO_API_KEY,
            "input": "base64",
            "file": file_b64,
            "filename": input_xls.name,
            "outputformat": "csv"
        }

        logger.debug("Enviando solicitud de conversión a Convertio API")
        response = requests.post(CONVERTIO_BASE_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            raise IngestionError(f"Error en la API de Convertio: {data}")

        convert_id = data["data"]["id"]
        logger.info(f"Conversión creada. ID: {convert_id}")

        # 3) Esperar a que la conversión termine
        status_url = f"{CONVERTIO_BASE_URL}/{convert_id}/status"

        while True:
            status_resp = requests.get(status_url)
            status_resp.raise_for_status()
            status_data = status_resp.json()

            step = status_data["data"]["step"]
            percent = status_data["data"]["step_percent"]

            logger.debug(f"Estado: {step} ({percent}%)")

            if step == "finish":
                break

            if step == "failed":
                raise IngestionError("La conversión falló en la API de Convertio")

            time.sleep(2)

        # 4) Descargar resultado
        logger.debug("Descargando resultado de la conversión")
        download_url = f"{CONVERTIO_BASE_URL}/{convert_id}/dl/base64"
        dl_resp = requests.get(download_url)
        dl_resp.raise_for_status()

        csv_bytes = base64.b64decode(dl_resp.json()["data"]["content"])

        # 5) Guardar archivo CSV
        with open(output_csv, "wb") as f:
            f.write(csv_bytes)

        logger.debug("Llamada a API exitosa")

    except requests.RequestException as e:
        logger.exception("Error de comunicación con la API de Convertio")
        raise IngestionError("Fallo en conversión XLS → CSV: error de comunicación con la API") from e
    except Exception as e:
        logger.exception("Error durante la conversión XLS → CSV")
        raise IngestionError("Fallo en conversión XLS → CSV") from e

    if not output_csv.exists():
        raise IngestionError("La conversión no generó el archivo CSV")

    logger.info("Conversión finalizada correctamente")
