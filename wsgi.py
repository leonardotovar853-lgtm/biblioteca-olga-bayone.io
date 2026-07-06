import sys
import os

# Asegurar que la carpeta BACKEND/ esté en el path de Python
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BACKEND'))

# Importar la aplicación Flask
from BACKEND.app import app

if __name__ == "__main__":
    app.run()