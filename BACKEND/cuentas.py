import json
import os
import uuid
from datetime import datetime
# Importamos todo lo necesario de Flask arriba, incluyendo render_template
from flask import request, jsonify, Flask, render_template
from flask_cors import CORS
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials, db as firebase_db

# URL Oficial de tu base de datos Firebase sin barra diagonal al final
FIREBASE_DB_URL = "https://biblioteca-olga-bayone-default-rtdb.firebaseio.com"

# Buscamos la carpeta DATA que está al mismo nivel que la carpeta BACKEND
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIREBASE_ADMIN_CREDENTIALS_PATH = os.path.join(BASE_DIR, "DATA", "biblioteca-olga-bayone-firebase-key.json")
FIREBASE_ADMIN_CREDENTIALS_JSON = None

class Usuario:
    def __init__(self, id_google, cedula, nombre, correo, foto_url, rol, anio_seccion, fecha_registro=None):
        self._id = str(id_google) if id_google else str(uuid.uuid4())
        self._nombre = nombre.strip().title() if nombre else None
        self._correo = correo.strip().lower() if correo else None
        self._foto_url = foto_url
        self._intereses = []
        self._fecha_registro = fecha_registro or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cedula = cedula
        self.rol = rol
        self.anio_seccion = anio_seccion
        
    def to_dict(self):
        return {
            'id': self.id,
            'cedula': self.cedula,
            'nombre': self.nombre,
            'correo': self.correo,
            'foto_url': self.foto_url,
            'rol': self.rol,
            'anio_seccion': self.anio_seccion,
            'intereses': self.intereses,
            'fecha_registro': self.fecha_registro
        }
        
    @property
    def id(self): return self._id

    @property
    def cedula(self): return self._cedula

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
    def nombre(self): return self._nombre
         
    @property
    def correo(self): return self._correo

    @property
    def foto_url(self): return self._foto_url

    @property
    def rol(self): return self._rol
    
    @rol.setter
    def rol(self, value):
        roles_validos = ["admin", "estudiante", "profesor"]
        if value and str(value).lower().strip() in roles_validos:
            self._rol = str(value).lower().strip()
        else:
            raise ValueError("Rol no válido. Debe ser 'admin', 'estudiante' o 'profesor'")   
        
    @property
    def anio_seccion(self): return self._anio_seccion

    @anio_seccion.setter
    def anio_seccion(self, value):
        anios_validos = ["1A", "1B","1C", "2A", "2B", "3A", "3B", "4A", "4B","4C","5A","5B","5C", "no_aplica", "No Aplica"]
        val_str = str(value).strip() if value is not None else ""
        if value and val_str in anios_validos:
            self._anio_seccion = val_str
        else:
            raise ValueError("Año/sección no válido o formato incorrecto.")
        
    @property
    def intereses(self): return self._intereses

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
    def fecha_registro(self): return self._fecha_registro


class Servidor:
    def __init__(self):
        self.db_url = FIREBASE_DB_URL
        self.firebase_app = self.init_firebase_admin()
        
        # Apuntamos correctamente a la carpeta FRONTEND para los estilos CSS e imágenes
        self.servidor = Flask(__name__, static_folder="../FRONTEND", static_url_path="/static")
        CORS(self.servidor)
        self.configurar_rutas()

    def init_firebase_admin(self):
        if firebase_admin._apps:
            return firebase_admin.get_app()

        if FIREBASE_ADMIN_CREDENTIALS_PATH and os.path.exists(FIREBASE_ADMIN_CREDENTIALS_PATH):
            cred = credentials.Certificate(FIREBASE_ADMIN_CREDENTIALS_PATH)
        elif FIREBASE_ADMIN_CREDENTIALS_JSON:
            try:
                cred = credentials.Certificate(json.loads(FIREBASE_ADMIN_CREDENTIALS_JSON))
            except Exception as e:
                raise RuntimeError(f"Credenciales de Firebase Admin no válidas: {str(e)}")
        else:
            raise RuntimeError(
                "No se encontraron credenciales de Firebase Admin. "
                "Configura GOOGLE_APPLICATION_CREDENTIALS o FIREBASE_ADMIN_CREDENTIALS."
            )

        return firebase_admin.initialize_app(cred, {
            'databaseURL': self.db_url
        })

    def agregar_usuario(self, usuario):
        if not isinstance(usuario, Usuario):
            raise ValueError("El objeto proporcionado no es una instancia de Usuario")
        
        usuario_existente = self.buscar_usuario_por_google_id(usuario.id)
        if usuario_existente:
            raise ValueError("El usuario ya existe en la base de datos.")

        try:
            ref = firebase_db.reference(f"usuarios/{usuario.id}")
            ref.set(usuario.to_dict())
            return "Usuario agregado exitosamente"
        except Exception as e:
            raise ValueError(f"Error al escribir en Firebase: {str(e)}")
        
    def buscar_usuario_por_google_id(self, google_id):
        try:
            ref = firebase_db.reference(f"usuarios/{google_id}")
            usuario = ref.get()
            return usuario if usuario else None
        except Exception:
            return None

    def verificar_token_firebase(self, id_token):
        if not id_token:
            raise ValueError("Token de Firebase no recibido")

        try:
            payload = firebase_auth.verify_id_token(id_token)
        except Exception as e:
            raise ValueError(f"Token de Firebase no válido o expirado: {str(e)}")

        proveedor = payload.get('firebase', {}).get('sign_in_provider')
        if proveedor and proveedor != 'google.com':
            raise ValueError("El inicio de sesión debe ser con Google")

        correo = payload.get('email', '')
        if not (correo.endswith('@olgabayone.com') or correo.endswith('@gmail.com')):
            raise ValueError("Solo se permiten cuentas institucionales autorizadas")

        return payload

    def configurar_rutas(self):
            # 1. RUTA PRINCIPAL: Catálogo dinámico para Alumnos (Filtra por Aprobados)
            @self.servidor.route('/')
            def inicio():
                try:
                    ref = firebase_db.reference("libros")
                    libros_data = ref.get() or {}
                    
                    libros_aprobados = []
                    for id_libro, info in libros_data.items():
                        if isinstance(info, dict) and info.get('estado') == 'Aprobado':
                            info['id'] = id_libro
                            libros_aprobados.append(info)
                    
                    return render_template("catalogo.html", libros=libros_aprobados)
                except Exception as e:
                    return f"Error al cargar el catálogo: {str(e)}", 500

            # 2. RUTA DEL ADMINISTRADOR: Panel de Control para subir PDFs
            @self.servidor.route('/admin-panel')
            def panel_administrador():
                return render_template("Panel_control.html")

            # --- TUS RUTAS DE API ACTUALES (Intactas) ---
            @self.servidor.route('/api/verificar-usuario', methods=['POST'])
            def verificar_usuario_endpoint():
                try:
                    data = request.get_json()
                    token = data.get('idToken')
                    payload = self.verificar_token_firebase(token)
                    firebase_uid = payload.get('uid')
                    usuario_existente = self.buscar_usuario_por_google_id(firebase_uid)
                    if usuario_existente:
                        return jsonify({"existe": True, "usuario": usuario_existente}), 200
                    else:
                        return jsonify({"existe": False, "mensaje": "Usuario nuevo, requiere registro"}), 200
                except Exception as e:
                    return jsonify({"error": str(e)}), 400

            @self.servidor.route('/api/registro-usuario', methods=['POST'])
            def registro_usuario_endpoint():
                try:
                    data = request.get_json()
                    token = data.get('idToken')
                    payload = self.verificar_token_firebase(token)
                    usuario = Usuario(
                        id_google=payload.get('uid'),
                        cedula=data.get('cedula'),
                        nombre=data.get('name') or payload.get('name'), 
                        correo=data.get('email') or payload.get('email'),
                        foto_url=data.get('picture') or payload.get('picture'),
                        rol=data.get('rol'),
                        anio_seccion=data.get('anio_seccion'), 
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

# Instanciamos la clase para configurar las rutas
servidor_biblioteca = Servidor()

# EXCLUSIVO PARA RENDER
instancia_servidor = servidor_biblioteca.servidor

if __name__ == "__main__":
    print("🚀 Servidor Flask (Local) escuchando en http://localhost:5000...")
    servidor_biblioteca.correr()