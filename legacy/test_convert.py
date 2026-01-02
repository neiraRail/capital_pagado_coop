import time
import base64
import requests

API_KEY = "2dae5621f2bcfb385f1db1f916b63223"  # Reemplaza con tu clave real
INPUT_FILE = "malos/septiembremalo.xls"   # Ruta al XLS de entrada
OUTPUT_FILE = "resultado.csv"



# 1) Leer archivo y codificar a base64
with open(INPUT_FILE, "rb") as f:
    file_bytes = f.read()

file_b64 = base64.b64encode(file_bytes).decode("ascii")

# 2) Crear conversión con input = base64
url = "https://api.convertio.co/convert"
payload = {
    "apikey": API_KEY,
    "input": "base64",
    "file": file_b64,
    "filename": INPUT_FILE,
    "outputformat": "csv"
}

response = requests.post(url, json=payload)
response.raise_for_status()
data = response.json()

if data.get("status") != "ok":
    raise RuntimeError(data)

convert_id = data["data"]["id"]
print("Conversión creada. ID:", convert_id)


# Esperar a que la conversión termine
status_url = f"https://api.convertio.co/convert/{convert_id}/status"

while True:
    status_resp = requests.get(status_url)
    status_resp.raise_for_status()
    status_data = status_resp.json()

    step = status_data["data"]["step"]
    percent = status_data["data"]["step_percent"]

    print(f"Estado: {step} ({percent}%)")

    if step == "finish":
        break

    if step == "failed":
        raise RuntimeError("La conversión falló")

    time.sleep(2)

# Descargar resultado
download_url = f"https://api.convertio.co/convert/{convert_id}/dl/base64"
dl_resp = requests.get(download_url)
dl_resp.raise_for_status()

csv_bytes = base64.b64decode(dl_resp.json()["data"]["content"])

with open("resultado.csv", "wb") as f:
    f.write(csv_bytes)

print("CSV descargado correctamente")
