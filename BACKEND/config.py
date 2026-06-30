import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'DATA')
BACKEND_DIR = os.path.join(BASE_DIR, 'BACKEND')
FRONTEND_DIR = os.path.join(BASE_DIR, 'FRONTEND')

# Credenciales
CREDENCIALES_PATH = os.path.join(DATA_DIR, 'credenciales.json')
FIREBASE_KEY_PATH = os.path.join(DATA_DIR, 'biblioteca-olga-bayone-firebase-key.json')

# Firebase
FIREBASE_DB_URL = "https://biblioteca-olga-bayone-default-rtdb.firebaseio.com"

# Google Sheets
SPREADSHEET_NAME = "Agregar Libro (Respuestas)"
BD_GENERAL_SHEET = "BD_General"

# Git
REPOSITORIO_DIR = BASE_DIR