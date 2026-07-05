import json
import os
import csv
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, send_file
import gspread
import pandas as pd
from config import CREDENCIALES_PATH, ENV_GSPREAD_CREDENTIALS, SPREADSHEET_NAME, BD_GENERAL_SHEET, MAPA_FORMULARIOS_ORIGEN
from logger import get_logger

logger = get_logger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
_cache_instance = None

def set_admin_cache(cache_instance):
    global _cache_instance
    _cache_instance = cache_instance

# =============================================================================
# CONEXIÓN GLOBAL A GOOGLE SHEETS (lazy connection)
# =============================================================================
_sheet_conexion = None

def get_sheet():
    global _sheet_conexion
    if _sheet_conexion is None:
        credenciales_json = os.environ.get(ENV_GSPREAD_CREDENTIALS)
        if credenciales_json:
            gc = gspread.service_account_from_dict(json.loads(credenciales_json))
        else:
            gc = gspread.service_account(filename=CREDENCIALES_PATH)
        sh = gc.open(SPREADSHEET_NAME)
        _sheet_conexion = sh.worksheet(BD_GENERAL_SHEET)
    return _sheet_conexion

def get_all_records():
    try:
        sheet = get_sheet()
        return sheet.get_all_records()
    except Exception as e:
        logger.error(f"Error leyendo BD_General: {e}")
        return []

def update_estado(fila_idx, nuevo_estado):
    try:
        sheet = get_sheet()
        COLUMNA_ESTADO = 18
        sheet.update_cell(fila_idx, COLUMNA_ESTADO, nuevo_estado)
        return True
    except Exception as e:
        logger.error(f"Error actualizando estado: {e}")
        return False

def eliminar_de_hoja_origen(tipo_recurso, titulo, autor):
    try:
        credenciales_json = os.environ.get(ENV_GSPREAD_CREDENTIALS)
        if credenciales_json:
            gc = gspread.service_account_from_dict(json.loads(credenciales_json))
        else:
            gc = gspread.service_account(filename=CREDENCIALES_PATH)
        sh = gc.open(SPREADSHEET_NAME)

        nombre_hoja = MAPA_FORMULARIOS_ORIGEN.get(tipo_recurso.lower())
        if not nombre_hoja:
            return False

        hoja_origen = sh.worksheet(nombre_hoja)
        registros = hoja_origen.get_all_records()
        for i, reg in enumerate(registros):
            t = str(reg.get('Titulo', reg.get('Título', ''))).strip().lower()
            a = str(reg.get('Autor', reg.get('Autor(es)', ''))).strip().lower()
            if t == titulo.lower() and a == autor.lower():
                hoja_origen.delete_rows(i + 2)
                logger.info(f"Eliminado de hoja origen '{nombre_hoja}' fila {i+2}")
                return True
        return False
    except Exception as e:
        logger.error(f"Error eliminando de hoja origen: {e}")
        return False

# =============================================================================
# RUTAS
# =============================================================================

@admin_bp.route('/')
def admin_panel():
    return render_template('admin_panel.html')

@admin_bp.route('/api/pendientes')
def api_pendientes():
    registros = get_all_records()
    pendientes = []
    for i, fila in enumerate(registros):
        estado = str(fila.get('Estado', '')).strip()
        if estado in ['', 'Pendiente']:
            pendientes.append({
                'fila': i + 2,
                'tipo': str(fila.get('Tipo de Recurso', 'Libro')).strip().capitalize(),
                'titulo': str(fila.get('Titulo', '')).strip().title(),
                'autor': str(fila.get('Autor', 'N/A')).strip().title(),
                'area': str(fila.get('Area de Conocimiento', 'General')).strip().title(),
                'nivel': str(fila.get('Nivel de Educacion', 'N/A')).strip().title(),
                'anio': str(fila.get('Anio de publicacion', 'N/A')).strip(),
                'enlace': str(fila.get('Enlace del recurso', '')).strip()
            })
    return jsonify(pendientes)

@admin_bp.route('/api/procesar', methods=['POST'])
def api_procesar():
    data = request.get_json()
    fila = data.get('fila')
    nuevo_estado = data.get('estado')
    tipo = data.get('tipo', '')
    titulo = data.get('titulo', '')
    autor = data.get('autor', '')

    if nuevo_estado == 'Rechazado':
        eliminar_de_hoja_origen(tipo, titulo, autor)

    if update_estado(fila, nuevo_estado):
        return jsonify({"status": "success", "message": f"Recurso {nuevo_estado}"})
    return jsonify({"status": "error", "message": "No se pudo actualizar"}), 500

@admin_bp.route('/api/stats')
def api_stats():
    registros = get_all_records()
    total = len(registros)
    pendientes = sum(1 for r in registros if str(r.get('Estado', '')).strip() in ['', 'Pendiente'])
    aprobados = sum(1 for r in registros if str(r.get('Estado', '')).strip() == 'Aprobado')
    rechazados = sum(1 for r in registros if str(r.get('Estado', '')).strip() == 'Rechazado')
    return jsonify({
        "total": total,
        "pendientes": pendientes,
        "aprobados": aprobados,
        "rechazados": rechazados
    })

@admin_bp.route('/api/exportar-csv')
def api_exportar_csv():
    registros = get_all_records()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Tipo", "Titulo", "Autor", "Area", "Nivel", "Anio", "Enlace", "Estado"])
    for r in registros:
        writer.writerow([
            r.get('Tipo de Recurso', ''),
            r.get('Titulo', ''),
            r.get('Autor', ''),
            r.get('Area de Conocimiento', ''),
            r.get('Nivel de Educacion', ''),
            r.get('Anio de publicacion', ''),
            r.get('Enlace del recurso', ''),
            r.get('Estado', '')
        ])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"reporte_admin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

@admin_bp.route('/api/recargar', methods=['POST'])
def api_recargar():
    from app import cargar_biblioteca
    try:
        if _cache_instance:
            _cache_instance.clear()
            logger.info("Cache de la biblioteca limpiada desde Admin API.")
        cargar_biblioteca()
        return jsonify({"status": "success", "message": "Biblioteca recargada correctamente"})
    except Exception as e:
        logger.error(f"Error al recargar biblioteca desde Admin API: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500