import sys
import os
from config import BACKEND_DIR, FRONTEND_DIR, TEMPLATES_DIR, DATA_DIR, BASE_DIR, TIPOS_MULTIMEDIA, FLASK_DEBUG, FLASK_HOST, FLASK_PORT

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

# Variable global para almacenar la biblioteca cargada (objeto complejo, NO se cachea)
biblioteca_global = None

def cargar_biblioteca():
    """Carga la biblioteca desde Google Sheets. NO se cachea porque retorna un objeto complejo.

    El cache de objetos con jerarquías (Libro, Tesis, GuiaEstudio, etc.) es frágil:
    la deserialización puede perder atributos como 'estado', 'id', etc.
    """
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


# --- Funciones auxiliares con caché para datos JSON (datos simples, seguras de cachear) ---

def get_libros_data_json():
    """Devuelve JSON de libros (no tesis) para JS del frontend. CACHEABLE (dato simple)."""
    if biblioteca_global:
        return json.dumps(biblioteca_global.exportar_libros())
    return "[]"

def get_recomendaciones_index():
    """Devuelve lista de primeros 4 libros aprobados para recomendaciones del index."""
    if biblioteca_global:
        recursos_aprobados = [r for r in biblioteca_global.lista_libros if r.estado == 'Aprobado']
        libros_aprobados = [r for r in recursos_aprobados if r.tipo == 'Libro']
        return libros_aprobados[:4]
    return []

def get_libros_aprobados():
    if biblioteca_global:
        recursos_aprobados = [r for r in biblioteca_global.lista_libros if r.estado == 'Aprobado']
        return [r for r in recursos_aprobados if r.tipo == 'Libro']
    return []

def get_tesis_aprobadas():
    if biblioteca_global:
        recursos_aprobados = [r for r in biblioteca_global.lista_libros if r.estado == 'Aprobado']
        return [r for r in recursos_aprobados if r.tipo == 'Tesis']
    return []

def get_multimedia_aprobada():
    if biblioteca_global:
        recursos_aprobados = [r for r in biblioteca_global.lista_libros if r.estado == 'Aprobado']
        return [r for r in recursos_aprobados if r.tipo in TIPOS_MULTIMEDIA]
    return []


# --- Rutas de la API (para recargar datos desde el Panel de Control) ---
@app.route('/api/recargar_datos', methods=['POST'])
def recargar_datos_api():
    try:
        cargar_biblioteca()
        return jsonify({"status": "success", "message": "Datos de la biblioteca recargados."}), 200
    except Exception as e:
        logger.error(f"Error al recargar datos via API: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# --- Rutas de las páginas web (sirven las plantillas Jinja2) ---
@app.route('/')
def index():
    recomendaciones = get_recomendaciones_index()
    libros_json = get_libros_data_json()
    return render_template('index.html',
                           recursos_recomendados=recomendaciones,
                           json_data=libros_json)

@app.route('/catalogo')
def catalogo():
    libros_aprobados = get_libros_aprobados()
    libros_json = get_libros_data_json()
    return render_template('catalogo.html',
                           recursos=libros_aprobados,
                           json_data=libros_json)

@app.route('/repositorio')
def repositorio():
    tesis_aprobadas = get_tesis_aprobadas()
    tesis_json = json.dumps([r.to_dict() for r in tesis_aprobadas]) if tesis_aprobadas else "[]"
    return render_template('repositorio.html',
                           recursos=tesis_aprobadas,
                           json_data=tesis_json)

@app.route('/multimedia')
def multimedia():
    multimedia_aprobada = get_multimedia_aprobada()
    multimedia_json = json.dumps([r.to_dict() for r in multimedia_aprobada]) if multimedia_aprobada else "[]"
    return render_template('multimedia.html',
                           recursos=multimedia_aprobada,
                           json_data=multimedia_json)

@app.route('/sobre_proyecto')
def sobre_proyecto():
    return render_template('sobre_proyecto.html')

@app.route('/agregar_libro')
def agregar_libro():
    return render_template('agregar_libro.html')


if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)