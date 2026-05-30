from urllib.parse import urlparse # Para validación de URLs
import uuid
import random # Lo mantienes por si acaso, aunque usaremos uuid

class RecursoAcademico:
    # Modelo de recursos académicos (libros, tesis, etc.).
    
    # Constantes de la clase (Años, Tipos y Niveles válidos)
    tipos_validos = {'Libro', 'Tesis'}
    años_validos = range(1900, 2026)
    nivel_validos = ['1er Año', '2do Año', '3er Año', '4to Año', '5to Año', 'General']
    
    def __init__(self, titulo, autor, editorial, area, nivel, link, link_portada, tipo, anio_publicacion, descripcion, id_existente=None):
        # Inicialización de variables privadas con valores por defecto
        self._titulo = 'Sin titulo'  
        self._autor = 'Anónimo'
        self._editorial = 'N/A'
        self._area = 'General'
        self._nivel = 'General'
        self._link = ''
        self._link_portada = ''
        self._tipo = 'Libro'
        self._anio_publicacion = 'Año desconocido'
        self._descripcion = 'Sin descripción'
        
        if id_existente and str(id_existente).strip() not in ['', 'nan', 'None']:
            self._id = str(id_existente)
        else:
            # Generamos un ID de 8 caracteres alfanuméricos únicos
            self._id = uuid.uuid4().hex[:8]
        
        # ✅ PRIMERO: Convertir el enlace de Drive
        link_portada_convertido = self._convertir_drive_url(link_portada)
        
        # ✅ DESPUÉS: Asignar usando setters (UNA SOLA VEZ)
        self.titulo = titulo
        self.autor = autor
        self.editorial = editorial
        self.area = area
        self.nivel = nivel
        self.link = link
        self.link_portada = link_portada_convertido  # ← ¡YA CONVERTIDO!
        self.tipo = tipo
        self.anio_publicacion = anio_publicacion
        self.descripcion = descripcion
    
    # Método estático para convertir URLs de Google Drive
    @staticmethod
    def _convertir_drive_url(url):
        """Convierte enlaces de Google Drive a formato de imagen."""
        if isinstance(url, str) and 'drive.google.com' in url and '/d/' in url:
            try:
                file_id = url.split('/d/')[1].split('/')[0]
                return f'https://drive.google.com/uc?export=view&id={file_id}'
            except IndexError:
                print(f"Advertencia: No se pudo convertir URL de Drive: {url}")
        return url
    
    # Propiedades y setters
    @property
    def titulo(self):
        return self._titulo
    
    @titulo.setter
    def titulo(self, valor):
        valor = str(valor).strip()
        if not valor or valor.lower() in ['none', 'nan', 'null', '']:
            self._titulo = 'Sin titulo'
        else:
            self._titulo = valor[:100]  # Limita a 100 caracteres para evitar títulos largos
    
    @property
    def autor(self):
        return self._autor
    
    @autor.setter
    def autor(self, valor):
        valor = str(valor).strip()
        if not valor or valor.lower() in ['none', 'nan', 'null', '']:
            self._autor = 'Anónimo'
        else:
            self._autor = valor[:100]  # Limita a 100 caracteres
    
    @property
    def tipo(self):
        return self._tipo
    
    @tipo.setter
    def tipo(self, valor):
        valor = str(valor).strip().capitalize()
        if valor in self.tipos_validos:
            self._tipo = valor
        else:
            print(f"Advertencia: Tipo '{valor}' no válido, asignando 'Libro'.")
            self._tipo = 'Libro'
    
    @property
    def editorial(self):
        return self._editorial
    
    @editorial.setter
    def editorial(self, valor):
        valor = str(valor).strip()
        if not valor or valor.lower() in ['none', 'nan', 'null', '']:
            self._editorial = 'N/A'
        else:
            self._editorial = valor[:100]  # Limita a 100 caracteres
    
    @property
    def area(self):
        return self._area
    
    @area.setter
    def area(self, valor):
        valor = str(valor).strip()
        if not valor or valor.lower() in ['none', 'nan', 'null', '']:
            self._area = 'General'
        else:
            self._area = valor[:100]  # Limita a 100 caracteres
    
    @property
    def anio_publicacion(self):
        return self._anio_publicacion
    
    @anio_publicacion.setter
    def anio_publicacion(self, valor):
        try:
            año = int(float(str(valor).strip()))
            if año in self.años_validos:
                self._anio_publicacion = str(año)
            else:
                print(f"Advertencia: Año '{año}' fuera de rango, asignando 'Año desconocido'.")
                self._anio_publicacion = 'Año desconocido'
        except (ValueError, TypeError):
            print(f"Advertencia: Valor de año inválido '{valor}', asignando 'Año desconocido'.")
            self._anio_publicacion = 'Año desconocido'
    
    @property
    def nivel(self):
        return self._nivel
    
    @nivel.setter
    def nivel(self, valor):
        valor = str(valor).strip()
        if valor in self.nivel_validos:
            self._nivel = valor
        else:
            print(f"Advertencia: Nivel '{valor}' no válido, asignando 'General'.")
            self._nivel = 'General'
    
    @property
    def link(self):
        return self._link
    
    @link.setter
    def link(self, valor):
        valor = str(valor).strip()
        parsed = urlparse(valor)
        if parsed.scheme in ['http', 'https'] and parsed.netloc:
            self._link = valor
        else:
            print(f"Advertencia: Link inválido '{valor}', asignando vacío.")
            self._link = ''
    
    @property
    def link_portada(self):
        return self._link_portada

    @link_portada.setter
    def link_portada(self, valor):
        # Si es string y no está vacío
        if isinstance(valor, str) and valor.strip():
            valor_limpio = valor.strip()
            # ✅ Solo guardar si empieza con http o es base64 (para no perder datos)
            if valor_limpio.startswith(('http://', 'https://', 'data:image')):
                self._link_portada = valor_limpio
            else:
                print(f"⚠️ Formato de imagen no soportado: {valor_limpio[:50]}...")
                self._link_portada = ''
        else:
            self._link_portada = ''
    
    @property
    def descripcion(self):
        return self._descripcion
    
    @descripcion.setter
    def descripcion(self, valor):
        valor = str(valor).strip()
        if not valor or valor.lower() in ['none', 'nan', 'null', '']:
            self._descripcion = 'Sin descripción'
        else:
            self._descripcion = valor[:500]  # Limita a 500 caracteres
    
    @property
    def id(self):  
        return self._id

    # Métodos y propiedades adicionales
    @property
    def es_tesis(self):
        return self._tipo == 'Tesis'
    
    def generar_tarjeta_html(self):
        # Sanitiza valores para evitar inyección
        area_safe = self._area.replace("'", "&#39;")
        tipo_safe = self._tipo.replace("'", "&#39;")
        titulo_safe = self._titulo.replace("'", "&#39;")
        autor_safe = self._autor.replace("'", "&#39;")
        anio_safe = self._anio_publicacion.replace("'", "&#39;")
        
        return f"""
                <div class='libro-card' data-category='{area_safe} {tipo_safe}' data-year='{self._nivel}' libro-id='{self._id}'>
                    <img src="{self._link_portada}">
                    <div class="badge-{self._tipo.lower()}">{tipo_safe}</div>
                    <h3>{titulo_safe}</h3>
                    <p class="autor-name">{autor_safe}</p>
                    <p class="año-public"><b>{anio_safe}</b></p>
                    
                    <div class="card-footer">
                        <button class="btn-flip">Ver Descricion</button>
                        <a href="{self._link}" target="_blank" class="btn-leer">Leer {tipo_safe}</a>
                        <button class="btn-like" onclick="darLike('{self._id}')">
                            ❤️ <span id="count-{self._id}">0</span>
                        </button>
                    </div>
                </div>
                """
    
    def to_dict(self):
        """Convierte el recurso a un diccionario para JSON."""
        return {
            'titulo': self._titulo,
            'autor': self._autor,
            'area': self._area,
            'nivel': self._nivel,
            'tipo': self._tipo,
            'anio_publicacion': self._anio_publicacion,
            'link': self._link,
            'link_portada': self._link_portada,
            'descripcion': self._descripcion,
            'ID': self._id
        }

class Biblioteca:
    def __init__(self, nombre):
        self.nombre = nombre
        self.lista_libros = []
    
    def agregar_recurso(self, recurso):
        if isinstance(recurso, RecursoAcademico):
            self.lista_libros.append(recurso)
        else:
            print(f"Advertencia: Intento de agregar recurso inválido: {type(recurso)}")
    
    # Métodos adicionales para extensibilidad
    def contar_recursos(self):
        return len(self.lista_libros)
    
    def buscar_por_tipo(self, tipo):
        return [r for r in self.lista_libros if r.tipo == tipo]
    
    def buscar_por_area(self, area):
        return [r for r in self.lista_libros if r.area == area]
    
    def buscar_por_nivel(self, nivel):
        return [r for r in self.lista_libros if r.nivel == nivel]
    
    def buscar_por_autor(self, autor):
        return [r for r in self.lista_libros if r.autor.lower() == autor.lower()]
    
    def buscar_por_anio(self, anio):
        return [r for r in self.lista_libros if r.anio_publicacion == str(anio)]
    
    def buscar_por_id(self, id):
        for r in self.lista_libros:
            if r.id == id:
                return r
        return None
    
    def recomendar_similares(self, recurso, limite=5):
        """Recomienda libros similares basados en autor, área y año."""
        similares = []
        # Por autor
        similares.extend([r for r in self.buscar_por_autor(recurso.autor) if r != recurso])
        # Por área
        similares.extend([r for r in self.buscar_por_area(recurso.area) if r != recurso and r not in similares])
        # Por año cercano (mismo año o +-1)
        try:
            anio = int(recurso.anio_publicacion)
            for offset in [-1, 0, 1]:
                similares.extend([r for r in self.buscar_por_anio(anio + offset) if r != recurso and r not in similares])
        except ValueError:
            pass
        # Remover duplicados y limitar
        return list(dict.fromkeys(similares))[:limite]
    
    def exportar_a_lista_dict(self):
        """Exporta la lista de libros a una lista de diccionarios para JSON."""
        return [libro.to_dict() for libro in self.lista_libros]
    
    def exportar_libros(self):
        """Exporta solo los libros (no tesis) a una lista de diccionarios."""
        return [libro.to_dict() for libro in self.lista_libros if not libro.es_tesis]
    def exportar_tesis(self):
        """Exporta solo las tesis a una lista de diccionarios."""
        return [libro.to_dict() for libro in self.lista_libros if libro.es_tesis]