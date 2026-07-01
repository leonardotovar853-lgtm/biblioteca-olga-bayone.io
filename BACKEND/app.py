from flask import Flask, render_template, jsonify, request
import os
import json
from admin_datos import limpieza_datos
from cuentas import cuentas_bp, init_firebase_admin_if_needed # Importamos el Blueprint y la inicialización de Firebase
import firebase_admin # Aseguramos que firebase_admin esté importado aquí

# Obtener la ruta base del proyecto para configurar carpetas estáticas y de plantillas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuración de la aplicación Flask
app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'BACKEND', 'templates'), # Plantillas ahora están en BACKEND/templates
            static_folder=os.path.join(BASE_DIR, 'FRONTEND'), # La carpeta FRONTEND completa es estática
            static_url_path='/FRONTEND') # Acceso a archivos estáticos vía /FRONTEND

# Registramos el Blueprint de cuentas_bp
app.register_blueprint(cuentas_bp, url_prefix='/api/cuentas') # Prefijo para las rutas de auth

# Variable global para almacenar la biblioteca cargada
biblioteca_global = None

def cargar_biblioteca():
    """
    Carga o recarga el objeto Biblioteca desde Google Sheets.
    """
    global biblioteca_global
    print("Cargando/Recargando datos de la biblioteca...")
    try:
        biblioteca_global = limpieza_datos()
        if biblioteca_global is None:
            print("Advertencia: No se pudo cargar la biblioteca. La web puede mostrar datos incompletos.")
        else:
            print(f"Biblioteca cargada con {len(biblioteca_global.lista_libros)} recursos.")
    except Exception as e:
        print(f"Error al cargar la biblioteca: {e}")
        biblioteca_global = None # Asegurar que esté nulo en caso de error

# --- Inicialización de Firebase Admin --- (Solo una vez al iniciar la app)
# Asegúrate de que las credenciales de Firebase estén configuradas correctamente.
# Se usará la función init_firebase_admin_if_needed de cuentas.py
init_firebase_admin_if_needed()

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
        recursos_aprobados = [r for r in biblioteca_global.lista_libros if r.estado == 'Aprobado']
        libros_aprobados = [r for r in recursos_aprobados if r.tipo == 'Libro']
        recomendaciones_index = libros_aprobados[:4]
        libros_data_json = json.dumps(biblioteca_global.exportar_libros())
    else:
        recomendaciones_index = []
    return render_template('index.html', recursos_recomendados=recomendaciones_index, json_data=libros_data_json)

@app.route('/catalogo')
def catalogo():
    recursos_aprobados = []
    libros_aprobados = []
    libros_data_json = "[]"
    if biblioteca_global:
        recursos_aprobados = [r for r in biblioteca_global.lista_libros if r.estado == 'Aprobado']
        libros_aprobados = [r for r in recursos_aprobados if r.tipo == 'Libro']
        libros_data_json = json.dumps(biblioteca_global.exportar_libros())
    return render_template('catalogo.html', recursos=libros_aprobados, json_data=libros_data_json)

@app.route('/repositorio')
def repositorio():
    recursos_aprobados = []
    tesis_aprobadas = []
    tesis_data_json = "[]"
    if biblioteca_global:
        recursos_aprobados = [r for r in biblioteca_global.lista_libros if r.estado == 'Aprobado']
        tesis_aprobadas = [r for r in recursos_aprobados if r.tipo == 'Tesis']
        tesis_data_json = json.dumps(biblioteca_global.exportar_tesis())
    return render_template('repositorio.html', recursos=tesis_aprobadas, json_data=tesis_data_json)

@app.route('/multimedia')
def multimedia():
    recursos_aprobados = []
    multimedia_aprobada = []
    multimedia_data_json = "[]"
    if biblioteca_global:
        recursos_aprobados = [r for r in biblioteca_global.lista_libros if r.estado == 'Aprobado']
        multimedia_aprobada = [r for r in recursos_aprobados if r.tipo in ['Guia', 'Video', 'Web']]
        multimedia_data_json = json.dumps(biblioteca_global.exportar_repositorio())
    return render_template('multimedia.html', recursos=multimedia_aprobada, json_data=multimedia_data_json)

@app.route('/sobre_proyecto')
def sobre_proyecto():
    return render_template('sobre_proyecto.html')

@app.route('/agregar_libro')
def agregar_libro():
    return render_template('agregar_libro.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
