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
            celda = self.worksheet.find(usuario.id)
            if celda:
                raise ValueError("El usuario ya existe en Google Sheets")
        except gspread.exceptions.CellNotFound:
            pass 
        except Exception as e:
            raise ValueError(f"Error al verificar usuario: {str(e)}")

        try:
            self.worksheet.append_row(usuario.a_lista())
            return "Usuario agregado exitosamente"
        except Exception as e:
            raise ValueError(f"Error al escribir en Google Sheets: {str(e)}")
        
    def obtener_DataFrame_usuarios(self):
        try:
            datos = self.worksheet.get_all_records()
            return pd.DataFrame(datos)
        except Exception as e:
            raise ValueError(f"Error al obtener usuarios: {str(e)}")
        
    def buscar_usuario_por_google_id(self, google_id):
        try:
            id_str = str(google_id)
            celda = self.worksheet.find(id_str)
            if celda:
                fila = celda.row
                datos = self.worksheet.row_values(fila)
                columnas = ['id', 'cedula', 'nombre', 'correo', 'foto_url', 'rol', 'año_seccion', 'intereses', 'fecha_registro']
                row_dict = dict(zip(columnas, datos))
                if row_dict.get('intereses'):
                    row_dict['intereses'] = [i.strip() for i in row_dict['intereses'].split(',') if i.strip()]
                return row_dict
            return None
        except gspread.exceptions.CellNotFound:
            return None
        except Exception as e:
            raise ValueError(f"Error al buscar usuario por ID: {str(e)}")

    def buscar_usuario_por_correo(self, correo):
        try:
            registros = self.worksheet.get_all_records()
            for row in registros:
                if str(row.get('correo', '')).lower() == str(correo).lower():
                    return row
            return None
        except Exception as e:
            raise ValueError(f"Error al buscar usuario por correo: {str(e)}")

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
        if payload.get('iss') not in ("accounts.google.com", "https://accounts.google.com"):
            raise ValueError("Emisor del token no válido")
        if not payload.get('email', '').endswith('@olgabayone.com'):
            raise ValueError("Solo se permiten cuentas institucionales @olgabayone.com")

        return payload

    def configurar_rutas(self):
        @self.servidor.route('/')
        def inicio():
            return "El servidor Biblioteca Olga Bayone esta activo y listo para recibir solicitudes."

        @self.servidor.route('/api/login-usuario', methods=['POST'])
        def login_usuario_endpoint():
            try:
                data = request.get_json()
                token = data.get('credential') or data.get('token')
                payload = self.verificar_token_google(token)

                usuario = self.buscar_usuario_por_google_id(payload.get('sub')) or self.buscar_usuario_por_correo(payload.get('email'))
                if usuario:
                    return jsonify({"mensaje": "Usuario autenticado", "usuario": usuario}), 200

                return jsonify({"error": "Usuario no registrado. Completa tu perfil."}), 404
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        @self.servidor.route('/api/registro-usuario', methods=['POST'])
        @self.servidor.route('/agregar_usuario', methods=['POST'])
        def registro_usuario_endpoint():
            try:
                data = request.get_json()
                token = data.get('credential') or data.get('token')
                payload = self.verificar_token_google(token)

                usuario = Usuario(
                    id_google=payload.get('sub'),
                    cedula=data.get('cedula'),
                    nombre=data.get('nombre') or payload.get('given_name') or payload.get('name'),
                    correo=payload.get('email'),
                    foto_url=payload.get('picture'),
                    rol=data.get('rol'),
                    año_seccion=data.get('año_seccion'),
                    fecha_registro=data.get('fecha_registro')
                )

                if data.get('intereses'):
                    usuario.intereses = data.get('intereses')

                self.agregar_usuario(usuario)
                return jsonify({"mensaje": "Usuario agregado exitosamente", "usuario": usuario.to_dict()}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        @self.servidor.route('/api/verificar-google', methods=['POST'])
        def verificar_google_endpoint():
            try:
                data = request.get_json()
                token = data.get('credential') or data.get('token')
                payload = self.verificar_token_google(token)
                return jsonify({"mensaje": "Token válido", "payload": payload}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 400

    def correr(self):
        self.servidor.run(debug=True, port=5000)

if __name__ == "__main__":
    ruta_credenciales = r"C:\Users\NEW DELL\Documents\PROGRAMACIÓN\PROYECTO_BIBLIOTECA_DIGITAL\DATA\credenciales.json" 
    mi_bot = Servidor(ruta_credenciales, "Agregar Libro (Respuestas)")
    print("🚀 Servidor de la Biblioteca Digital Inteligente iniciado...")
    mi_bot.correr()