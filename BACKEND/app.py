import sys
import os
from config import BACKEND_DIR, FRONTEND_DIR, TEMPLATES_DIR, DATA_DIR, BASE_DIR, TIPOS_MULTIMEDIA, FLASK_DEBUG
from recomendaciones import obtener_recursos_para_recomendacion
# Añadir esta carpeta (BACKEND/) al path para que los imports funcionen en Render
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, jsonify, request
import json
from admin_datos import limpieza_datos
from cuentas import cuentas_bp, init_firebase_admin_if_needed
from admin_api import admin_bp
from logger import get_logger
import firebase_admin

logger = get_logger(__name__)


# Configuración de la aplicación Flask
app = Flask(__name__, 
            template_folder=TEMPLATES_DIR,
            static_folder=FRONTEND_DIR,
            static_url_path='/static')

# Registramos el Blueprint de cuentas_bp
app.register_blueprint(cuentas_bp, url_prefix='/api/cuentas')

app.register_blueprint(admin_bp, url_prefix='/admin')

# Variable global para almacenar la biblioteca cargada
biblioteca_global = None

def cargar_biblioteca():
    global biblioteca_global
    logger.info("Cargando/Recargando datos de la biblioteca...")
    try:
        biblioteca_global = limpieza_datos()
        if biblioteca_global is None:
            logger.warning("No se pudo cargar la biblioteca. La web puede mostrar datos incompletos.")
        else:
            logger.info(f"Biblioteca cargada con {len(biblioteca_global.lista_libros)} recursos.")
    except Exception as e:
        logger.error(f"Error al cargar la biblioteca: {e}")
        biblioteca_global = None

# --- Inicialización de Firebase Admin ---
try:
    init_firebase_admin_if_needed()
    logger.info("Firebase inicializado correctamente")
except Exception as e:
    logger.warning(f"Firebase no se pudo inicializar (autenticacion no disponible): {e}")

# Cargar la biblioteca al iniciar la aplicación
cargar_biblioteca()

# --- Rutas de la API (para recargar datos desde el Panel de Control) ---
@app.route('/api/recargar_datos', methods=['POST'])
def recargar_datos_api():
    try:
        cargar_biblioteca()
        return jsonify({"status": "success", "message": "Datos de la biblioteca recargados."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Rutas de las páginas web (sirven las plantillas Jinja2) ---
@app.route('/')
def index():
    recursos_aprobados = []
    libros_data_json = "[]"
if biblioteca_global:
        # Ahora usamos obtener_recursos_para_recomendacion que devuelve una lista de diccionarios
        todos_los_recursos_aprobados = obtener_recursos_para_recomendacion()
        
        # Para la sección de recomendaciones del index, filtramos libros y tomamos los primeros 4
        libros_aprobados = [r for r in todos_los_recursos_aprobados if r.get('tipo') == 'Libro']
        recomendaciones_index = libros_aprobados[:4]
        
        # Para el json_data, pasamos todos los libros (no tesis, etc.) para el buscador de JS
        libros_data_json = json.dumps([r for r in todos_los_recursos_aprobados if r.get('tipo') != 'Tesis'])
    else:
        recomendaciones_index = []
        libros_data_json = "[]"
    return render_template('index.html', recursos_recomendados=recomendaciones_index, json_data=libros_data_json)

@app.route('/catalogo')
def catalogo():
    recursos_aprobados_dicts = obtener_recursos_para_recomendacion()
        libros_aprobados = [r for r in recursos_aprobados_dicts if r.get('tipo') == 'Libro']
        libros_data_json = json.dumps([r for r in recursos_aprobados_dicts if r.get('tipo') != 'Tesis'])
    return render_template('catalogo.html', recursos=libros_aprobados, json_data=libros_data_json)

@app.route('/repositorio')
def repositorio():
    recursos_aprobados_dicts = obtener_recursos_para_recomendacion()
        tesis_aprobadas = [r for r in recursos_aprobados_dicts if r.get('tipo') == 'Tesis']
        tesis_data_json = json.dumps(tesis_aprobadas)
    return render_template('repositorio.html', recursos=tesis_aprobadas, json_data=tesis_data_json)

@app.route('/multimedia')
def multimedia():
    recursos_aprobados_dicts = obtener_recursos_para_recomendacion()
        multimedia_aprobada = [r for r in recursos_aprobados_dicts if r.get('tipo') in TIPOS_MULTIMEDIA]
        multimedia_data_json = json.dumps(multimedia_aprobada)
    return render_template('multimedia.html', recursos=multimedia_aprobada, json_data=multimedia_data_json)

@app.route('/sobre_proyecto')
def sobre_proyecto():
    return render_template('sobre_proyecto.html')

@app.route('/agregar_libro')
def agregar_libro():
    return render_template('agregar_libro.html')

if __name__ == '__main__':
    from config import FLASK_HOST, FLASK_PORT
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
