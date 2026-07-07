import os

# =============================================================================
# RUTAS DEL PROYECTO
# =============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'DATA')
BACKEND_DIR = os.path.join(BASE_DIR, 'BACKEND')
FRONTEND_DIR = os.path.join(BASE_DIR, 'FRONTEND')
TEMPLATES_DIR = os.path.join(BACKEND_DIR, 'templates')

# =============================================================================
# CREDENCIALES (Archivos locales)
# =============================================================================
CREDENCIALES_PATH = os.path.join(DATA_DIR, 'credenciales.json')
FIREBASE_KEY_PATH = os.path.join(DATA_DIR, 'biblioteca-olga-bayone-firebase-key.json')

# =============================================================================
# VARIABLES DE ENTORNO (Render / Producción)
# =============================================================================
ENV_FIREBASE_CREDENTIALS = "FIREBASE_ADMIN_CREDENTIALS"
ENV_GSPREAD_CREDENTIALS = "GSPREAD_CREDENTIALS"

# =============================================================================
# FIREBASE
# =============================================================================
FIREBASE_DB_URL = "https://biblioteca-olga-bayone-default-rtdb.firebaseio.com"

# =============================================================================
# GOOGLE SHEETS
# =============================================================================
SPREADSHEET_NAME = "Agregar Libro (Respuestas)"
BD_GENERAL_SHEET = "BD_General"

# Mapeo de formularios por tipo de recurso
FORMULARIOS = {
    'Form_Libros': 'Libro',
    'Form_Tesis': 'Tesis',
    'Form_Guias': 'Guia',
    'Form_Videos': 'Video',
    'Form_Web': 'Web'
}

MAPA_FORMULARIOS_ORIGEN = {
    'libro': 'Form_Libros',
    'tesis': 'Form_Tesis',
    'guia': 'Form_Guias',
    'video': 'Form_Videos',
    'web': 'Form_Web'
}

# =============================================================================
# SERVIDOR
# =============================================================================
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# URL base del Panel de Control (local o Render)
PANEL_FLASK_URL = "http://localhost:5000"

# =============================================================================
# GIT
# =============================================================================
REPOSITORIO_DIR = BASE_DIR

# =============================================================================
# CATEGORÍAS Y NIVELES
# =============================================================================
AREAS_LIBROS = [
    "Matemática",
    "Castellano y Literatura",
    "Ciencias Naturales (Física, Química y Biología general)",
    "Ciencias Sociales",
    "Historia",
    "Informática y Tecnologia",
    "Ingles y otras lenguas",
    "Arte y Patrimonio"
]

AREAS_TESIS = [
    "Salud",
    "Educación",
    "Orientación Vocacional",
    "Tecnología",
    "Ciencias",
    "Social"
]

AREAS_MULTIMEDIA = AREAS_LIBROS  # Mismas áreas que libros

NIVELES_EDUCACION = [
    "1er Año",
    "2do Año",
    "3er Año",
    "4to Año",
    "5to Año",
    "General"
]

TIPOS_MULTIMEDIA = ["Guia", "Video", "Web"]

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
