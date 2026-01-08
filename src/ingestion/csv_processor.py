# src/ingestion/csv_processor.py

import math
import pandas as pd
from pathlib import Path
from typing import Optional
from src.utils.exceptions import IngestionError
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

def tonumberNeg(text: str) -> int:
    text = text.replace('.', '')
    text = text.replace(',', '')
    return -int(text)

def tonumberPos(text: str) -> int:
    text = text.replace('.', '')
    text = text.replace(',', '')
    return int(text)


def regularizar_nombre(x, base: Optional[pd.DataFrame] = None, diccionario: Optional[pd.DataFrame] = None) -> str:
    """
    Regulariza el nombre de un socio basándose en nombre_1 y nombre_2.
    
    Args:
        x: Serie de pandas con las columnas: rut, nombre_1, nombre_2
        base: DataFrame opcional con columnas "Rut" y "Nombre" para búsqueda
        diccionario: DataFrame opcional con columnas "Rut" y "Nombre" para búsqueda
    
    Returns:
        str: Nombre regularizado
    """
    rut = x["rut"]
    nombre_1 = x["nombre_1"]
    nombre_2 = x["nombre_2"]
    
    # Caso cero, donde ambos son iguales, se queda el primero
    if nombre_1 == nombre_2:
        return nombre_1

    # Primer caso, donde ambos tienen valor, nos quedamos con el más largo
    if (nombre_1 != nombre_2) and pd.notna(nombre_1) and pd.notna(nombre_2):
        return nombre_1 if len(nombre_1) > len(nombre_2) else nombre_2

    # Segundo caso, donde solo hay nombre_1, nos quedamos con nombre_1
    if (nombre_1 != nombre_2) and pd.notna(nombre_1) and pd.isna(nombre_2):
        return nombre_1

    # Tercer caso, donde solo hay nombre_2, nos quedamos con nombre_2
    if (nombre_1 != nombre_2) and pd.isna(nombre_1) and pd.notna(nombre_2):
        return nombre_2

    # Cuarto caso, donde no hay data, hay que ir a buscar a la base de datos
    if (nombre_1 != nombre_2) and pd.isna(nombre_1) and pd.isna(nombre_2):
        # Intentar primero con la base si está disponible
        if base is not None:
            serie = base.loc[base["Rut"].str.strip() == str(rut).strip(), "Nombre"]
            if not serie.empty:
                return serie.iloc[0]

        # Si no se encontró en la base, intentar con el diccionario si está disponible
        if diccionario is not None:
            serie = diccionario.loc[diccionario["Rut"].str.strip() == str(rut).strip(), "Nombre"]
            if not serie.empty:
                return serie.iloc[0]
        
        # Si no se encontró en ningún archivo de referencia, retornar "No está"
        return "No está"


def process_csv(
    csv_path: Path,
    delimiter: str = ",",
    base_path: Optional[Path] = None,
    diccionario_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Procesa un archivo CSV convertido desde XLS y lo transforma en un DataFrame bien formado.
    
    Esta función lee el CSV resultante de la conversión, aplica las transformaciones necesarias
    para estructurar los datos correctamente y devuelve un DataFrame listo para el siguiente paso
    del pipeline (comparación de diferencias).
    
    Args:
        csv_path: Ruta al archivo CSV a procesar
        delimiter: Delimitador del CSV (por defecto ",")
        base_path: Ruta opcional al archivo CSV de base para regularización de nombres
        diccionario_path: Ruta opcional al archivo CSV de diccionario para regularización de nombres
    
    Returns:
        pd.DataFrame: DataFrame procesado con las columnas: rut, nombre_1, tipo, nombre_2, 
                     debitos, creditos, saldo, categoria, nombre
    
    Raises:
        IngestionError: Si el archivo no existe o hay un error en el procesamiento
    """
    logger.info(f"Procesando archivo CSV: {csv_path.name}")
    
    if not csv_path.exists():
        raise IngestionError(f"Archivo CSV no encontrado: {csv_path}")
    
    try:
        # Leer CSV empezando desde la fila 12 (header=12)
        df = pd.read_csv(csv_path, delimiter=delimiter, header=12)
        logger.debug(f"CSV leído con {len(df)} filas")
        
        # Eliminar la última fila
        df = df.iloc[:-1]
        
        # Filtrar filas que no contengan "/" en la columna "Vencto."
        clean_df = df[~df["Vencto."].str.contains("/").fillna(False)].reset_index(drop=True)
        logger.debug(f"Después de filtrar: {len(clean_df)} filas")
        
        # Crear "join_key" para juntar ambas filas por socio más adelante
        clean_df["join_key"] = pd.Series(clean_df.index).apply(lambda x: math.floor(x/2))
        
        # DataFrame de rut y nombre
        df_principal = clean_df.iloc[::2].reset_index(drop=True)
        df_principal = df_principal[["TP", "Vencto.", "Detalle", "join_key"]]
        df_principal.columns = ['rut', 'nombre_1', 'tipo', 'join_key']
        df_principal = df_principal.set_index("join_key")
        
        # DataFrame de nombre y totales
        df_secundario = clean_df.iloc[1::2].reset_index(drop=True)
        df_secundario = df_secundario[["TP.1", "Unnamed: 8", "Créditos", "Saldo", "Unnamed: 11", "join_key"]]
        df_secundario.columns = ['nombre_2', 'debitos', 'creditos', 'saldo', 'categoria', 'join_key']
        df_secundario = df_secundario.set_index("join_key")
        df_secundario["debitos"] = df_secundario["debitos"].fillna('0').apply(tonumberPos)
        df_secundario["creditos"] = df_secundario["creditos"].fillna('0').apply(tonumberPos)
        df_secundario["saldo"] = df_secundario["saldo"].apply(tonumberNeg)
        df_secundario["categoria"] = df_secundario["categoria"].fillna('')
        
        # Mezclar los 2 dataframes
        df_final = df_principal.join(df_secundario)
        df_final = df_final.reset_index(drop=True)
        
        # Cargar archivos de referencia si están disponibles
        base = None
        diccionario = None
        
        if base_path and base_path.exists():
            logger.debug(f"Cargando archivo base: {base_path}")
            base = pd.read_csv(base_path, index_col="Unnamed: 0")
        
        if diccionario_path and diccionario_path.exists():
            logger.debug(f"Cargando diccionario: {diccionario_path}")
            diccionario = pd.read_csv(diccionario_path)
        
        # Aplicar regularización de nombres (siempre se aplica, independientemente de los archivos de referencia)
        logger.debug("Aplicando regularización de nombres")
        df_final["nombre"] = df_final.apply(
            regularizar_nombre, 
            axis=1, 
            base=base, 
            diccionario=diccionario
        )
        
        # Validar que no queden nombres sin resolver
        nombres_sin_resolver = df_final[df_final["nombre"] == "No está"]
        if not nombres_sin_resolver.empty:
            ruts_faltantes = nombres_sin_resolver["rut"].unique().tolist()
            ruts_faltantes_str = ", ".join(map(str, ruts_faltantes))
            error_msg = (
                f"Se encontraron {len(nombres_sin_resolver)} registros sin nombre resuelto. "
                f"RUTs afectados: {ruts_faltantes_str}. "
                f"Por favor, agregue estos nombres al diccionario de referencia."
            )
            logger.error(error_msg)
            raise IngestionError(error_msg)
        
        # Eliminar filas con categoría vacía o nula
        logger.debug("Eliminando filas con categoría vacía o nula")
        filas_antes_filtro = len(df_final)
        
        # Filtrar filas donde categoría no sea vacía ni nula
        df_final = df_final[
            (df_final["categoria"].notna()) & 
            (df_final["categoria"] != "")
        ].reset_index(drop=True)
        
        filas_despues_filtro = len(df_final)
        filas_eliminadas = filas_antes_filtro - filas_despues_filtro
        
        if filas_eliminadas > 0:
            logger.info(f"Se eliminaron {filas_eliminadas} filas con categoría vacía o nula. "
                       f"Filas antes: {filas_antes_filtro}, filas después: {filas_despues_filtro}")
        
        # Agrupar filas duplicadas por nombre, sumando valores numéricos y manteniendo el primer rut
        logger.debug("Agrupando filas duplicadas por nombre")
        filas_antes = len(df_final)
        
        # Definir funciones de agregación
        agg_dict = {
            'rut': 'first',  # Mantener el primer rut
            'nombre_1': 'first',  # Mantener el primer nombre_1
            'tipo': 'first',  # Mantener el primer tipo
            'nombre_2': 'first',  # Mantener el primer nombre_2
            'debitos': 'sum',  # Sumar debitos
            'creditos': 'sum',  # Sumar creditos
            'saldo': 'sum',  # Sumar saldo
            'categoria': 'first',  # Mantener la primera categoria
            'nombre': 'first'  # Mantener el nombre (debe ser igual en todas las filas del grupo)
        }
        
        df_final = df_final.groupby('nombre', as_index=False).agg(agg_dict)
        filas_despues = len(df_final)
        
        if filas_antes != filas_despues:
            logger.info(f"Se agruparon {filas_antes - filas_despues} filas duplicadas. "
                       f"Filas antes: {filas_antes}, filas después: {filas_despues}")
        
        logger.info(f"Procesamiento completado. DataFrame final con {len(df_final)} filas")
        return df_final
        
    except KeyError as e:
        logger.exception(f"Error: columna esperada no encontrada en el CSV: {e}")
        raise IngestionError(f"El CSV no tiene el formato esperado. Columna faltante: {e}")
    except Exception as e:
        logger.exception("Error durante el procesamiento del CSV")
        raise IngestionError(f"Fallo en procesamiento del CSV: {e}") from e

