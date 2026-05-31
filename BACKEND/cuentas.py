import requests
import json
import flask
import os
import gspread
import pandas as pd
import uuid
from datetime import datetime
from flask import request, jsonify, Flask
from flask_cors import CORS

GOOGLE_CLIENT_ID = "520347031267-ph0fosq8l2ngoinasnm4b914vnrbqk1k.apps.googleusercontent.com"

class Usuario:
    def __init__(self, id_google, cedula, nombre, correo, foto_url, rol, año_seccion, fecha_registro=None):
        # 1. Inicializamos las variables internas directamente con valores limpios
        self._id = str(id_google) if id_google else str(uuid.uuid4())
        self._nombre = nombre.strip().title() if nombre else None  # .title() maneja Nombres y Apellidos
        self._correo = correo.strip().lower() if correo else None
        self._foto_url = foto_url
        self._intereses = []
        self._fecha_registro = fecha_registro or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 2. Las variables que requieren validaciones estrictas las pasamos por sus setters
        self.cedula = cedula
        self.rol = rol
        self.año_seccion = año_seccion
        
    def to_dict(self):
        return {
            'id': self._id,
            'cedula': self._cedula,
            'nombre': self._nombre,
            'correo': self._correo,
            'foto_url': self._foto_url,
            'rol': self._rol,
            'año_seccion': self._año_seccion,
            'intereses': self._intereses,
            'fecha_registro': self._fecha_registro
        }

    def a_lista(self):
        intereses_texto = ", ".join(self._intereses) if self._intereses else ""
        return [
            self._id, 
            self._cedula, 
            self._nombre, 
            self._correo, 
            self._foto_url, 
            self._rol, 
            self._año_seccion, 
            intereses_texto, 
            self._fecha_registro
        ]
        
    @property
    def id(self):
        return self._id

    @property
    def cedula(self):
        return self._cedula

    @cedula.setter
    def cedula(self, value):    
        cedula_str = str(value).strip() if value else None
        if not cedula_str or not cedula_str.isdigit():
            raise ValueError("La cédula debe contener solo números.")
        if not (7 <= len(cedula_str) <= 9):
            raise ValueError("La cédula debe tener entre 7 y 9 dígitos.")
        if int(cedula_str) <= 0:
            raise ValueError("La cédula no puede ser negativa o cero.")
        self._cedula = int(cedula_str)

    @property
    def nombre(self):
        return self._nombre
         
    @property
    def correo(self):
        return self._correo

    @property
    def foto_url(self):
        return self._foto_url

    @property
    def rol(self):
        return self._rol
    
    @rol.setter
    def rol(self, value):
        roles_validos = ["admin", "estudiante", "profesor"]
        if value and str(value).lower().strip() in roles_validos:
            self._rol = str(value).lower().strip()
        else:
            raise ValueError("Rol no válido. Debe ser 'admin', 'estudiante' o 'profesor'")   
        
    @property
    def año_seccion(self):
        return self._año_seccion

    @año_seccion.setter
    def año_seccion(self, value):
        anios_validos = ["1A", "1B","1C", "2A", "2B", "3A", "3B", "4A", "4B","4C","5A","5B","5C", "no_aplica", "No Aplica"]
        val_str = str(value).strip()
        if value and val_str in anios_validos:
            self._año_seccion = val_str
        else:
            raise ValueError("Año/sección no válido o formato incorrecto.")
        
    @property
    def intereses(self):
        return self._intereses

    @intereses.setter
    def intereses(self, value):
        intereses_validos = ["Ciencia Ficción","Matemáticas", "Fantasía", "Misterio", "Romance", "Aventura", "No Ficción", "Historia", "Tecnología"]
        if isinstance(value, list):
            if all(isinstance(interes, str) for interes in value):
                if all(interes in intereses_validos for interes in value):
                    self._intereses = value
                    return
        raise ValueError("Los intereses deben ser una lista de strings válidos.")

    @property
    def fecha_registro(self):
        return self._fecha_registro


# ... (Tu clase Usuario se mantiene exactamente IGUAL, está perfecta)

class Servidor:
    def __init__(self, ruta_credenciales, nombre_hoja):
        self.ruta_credenciales = ruta_credenciales
        self.nombre_hoja = nombre_hoja
        self.gc = gspread.service_account(filename=self.ruta_credenciales)
        self.sh = self.gc.open(self.nombre_hoja)
        self.worksheet = self.sh.worksheet("Usuarios") 
        
        self.servidor = Flask(__name__) 
        CORS(self.servidor) 
        self.configurar_rutas()

    def agregar_usuario(self, usuario):
        if not isinstance(usuario, Usuario):
            raise ValueError("El objeto proporcionado no es una instancia de Usuario")
        
        try:
            # gspread requiere strings para buscar
            celda = self.worksheet.find(str(usuario.id))
            if celda:
                raise ValueError("El usuario ya existe en la base de datos.")
        except gspread.exceptions.CellNotFound:
            pass 

        try:
            self.worksheet.append_row(usuario.a_lista())
            return "Usuario agregado exitosamente"
        except Exception as e:
            raise ValueError(f"Error al escribir en Google Sheets: {str(e)}")
        
    def buscar_usuario_por_google_id(self, google_id):
        try:
            id_str = str(google_id)
            celda = self.worksheet.find(id_str)
            if celda:
                fila = celda.row
                datos = self.worksheet.row_values(fila)
                columnas = ['id', 'cedula', 'nombre', 'correo', 'foto_url', 'rol', 'año_seccion', 'intereses', 'fecha_registro']
                
                # Asegurar que la longitud coincida por si faltan campos al final
                while len(datos) < len(columnas):
                    datos.append("")
                    
                row_dict = dict(zip(columnas, datos))
                if row_dict.get('intereses'):
                    row_dict['intereses'] = [i.strip() for i in row_dict['intereses'].split(',') if i.strip()]
                return row_dict
            return None
        except gspread.exceptions.CellNotFound:
            return None

    def verificar_token_google(self, id_token):
        if not id_token:
            raise ValueError("Token de Google no recibido")

        token_info_url = "https://oauth2.googleapis.com/tokeninfo"
        resp = requests.get(token_info_url, params={"id_token": id_token}, timeout=10)
        if resp.status_code != 200:
            raise ValueError("Token de Google no válido o expirado")

        payload = resp.json()
        if payload.get('aud') != GOOGLE_CLIENT_ID:
            raise ValueError("Token de Google no corresponde al cliente")
        
        # ⚠️ NOTA DE DESARROLLO: Cambié temporalmente esto para tus pruebas con cuentas @gmail.com
        # Cuando lo entregues en el colegio, vuelve a cambiar '@gmail.com' por '@olgabayone.com'
        correo = payload.get('email', '')
        if not (correo.endswith('@olgabayone.com') or correo.endswith('@gmail.com')):
            raise ValueError("Solo se permiten cuentas institucionales autorizadas")

        return payload

    def configurar_rutas(self):
        @self.servidor.route('/')
        def inicio():
            return "El servidor Biblioteca Olga Bayone está activo."

        # CORRECCIÓN 1: Endpoint unificado de verificación y Login mediante TOKEN
        @self.servidor.route('/api/verificar-usuario', methods=['POST'])
        def verificar_usuario_endpoint():
            try:
                data = request.get_json()
                token = data.get('credential')
                
                # Desencriptamos el token directo en el backend de forma segura
                payload = self.verificar_token_google(token)
                google_id = payload.get('sub')

                usuario_existente = self.buscar_usuario_por_google_id(google_id)
                
                if usuario_existente:
                    return jsonify({"existe": True, "usuario": usuario_existente}), 200
                else:
                    return jsonify({"existe": False, "mensaje": "Usuario nuevo, requiere registro"}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        # CORRECCIÓN 2: Registro adaptado a las variables que envía el Javascript
        @self.servidor.route('/api/registro-usuario', methods=['POST'])
        @self.servidor.route('/agregar_usuario', methods=['POST'])
        def registro_usuario_endpoint():
            try:
                data = request.get_json()
                token = data.get('credential')
                payload = self.verificar_token_google(token)

                # Mapeo exacto de nombres (JS manda 'anio_seccion' -> Python lee 'anio_seccion')
                usuario = Usuario(
                    id_google=payload.get('sub'),
                    cedula=data.get('cedula'),
                    nombre=payload.get('name'), # Usamos el nombre verificado por Google
                    correo=payload.get('email'),
                    foto_url=payload.get('picture'),
                    rol=data.get('rol'),
                    año_seccion=data.get('anio_seccion'), # ¡Arreglado el choque de nombres!
                    fecha_registro=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

                if data.get('intereses'):
                    usuario.intereses = data.get('intereses')

                self.agregar_usuario(usuario)
                return jsonify({"mensaje": "Usuario registrado con éxito", "usuario": usuario.to_dict()}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 400

    def correr(self):
        self.servidor.run(debug=True, port=5000)

if __name__ == "__main__":
    ruta_credenciales = r"C:\Users\NEW DELL\Documents\PROGRAMACIÓN\PROYECTO_BIBLIOTECA_DIGITAL\DATA\credenciales.json" 
    mi_bot = Servidor(ruta_credenciales, "Agregar Libro (Respuestas)")
    print("🚀 Servidor Flask escuchando en http://localhost:5000...")
    mi_bot.correr()