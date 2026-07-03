import logging
import sys
from config import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT

# Configuración global del logger
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    stream=sys.stdout
)

def get_logger(name):
    logger = logging.getLogger(name)
    return logger