from admin_datos import limpieza_datos
from modelos import Biblioteca
import pandas # pandas no se usa directamente aquí, pero lo dejo por si acaso
from logger import get_logger

logger = get_logger(__name__)

# Data Recursos (inicialización lazy)
_biblioteca_cache = None

def obtener_biblioteca():
    global _biblioteca_cache
    if _biblioteca_cache is None:
        logger.info("Cargando biblioteca para recomendaciones...")
        _biblioteca_cache = limpieza_datos()
    return _biblioteca_cache

def obtener_recursos_para_recomendacion():
    """
    Devuelve una lista de diccionarios de recursos aprobados para usar en recomendaciones.
    """
    biblioteca = obtener_biblioteca()
    if biblioteca:
        # Convertimos a dicts solo los recursos aprobados para la UI
        recursos_aprobados = [r.to_dict() for r in biblioteca.lista_libros if r.estado == 'Aprobado']
        logger.info(f"Recursos disponibles para recomendación: {len(recursos_aprobados)}")
        return recursos_aprobados
    logger.warning("No se pudo cargar la biblioteca para obtener recomendaciones.")
    return []

# La llamada directa a convertir_data(biblioteca) se elimina, ya que la función es un API.