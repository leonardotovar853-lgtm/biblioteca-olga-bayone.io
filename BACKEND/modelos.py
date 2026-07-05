from urllib.parse import urlparse
import uuid
import random 
import time
from logger import get_logger

logger = get_logger(__name__)

class RecursoAcademico:
    # Modelo de recursos académicos (libros, tesis, etc.).
    anio_actual = time.localtime().tm_year
    # Constantes de la clase (Años, Tipos y Niveles válidos)
    tipos_validos = ['Libro', 'Tesis', 'Guia', 'Video', 'Web']
    años_validos = range(1900, anio_actual + 1)
    nivel_validos = ['1er Año', '2do Año', '3er Año', '4to Año', '5to Año', 'General']
    
    def __init__(self, titulo, autor, editorial, area, nivel, link, link_portada, tipo, anio_publicacion, descripcion, id_existente=None, estado='Pendiente'):
        # Inicialización de variables privadas con valores por defecto
        self._titulo = 'Sin titulo'  
        self._autor = 'Anónimo'
        self._editorial = 'N/A'
        self._area = 'General'
        self._nivel = 'General'
        self._link = ''
        self._link_portada = ''
        self._anio_publicacion = 'Año desconocido'
        self._descripcion = 'Sin descripción'
        self._estado = estado

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
        self.link_portada = link_portada_convertido  
        self.anio_publicacion = anio_publicacion
        self.descripcion = descripcion
        self.tipo = tipo  
        
    @staticmethod
    def _generar_portada_automatica(link, tipo):
        """
        Determina la URL de la portada de forma automática y óptima 
        según el enlace del recurso y su tipo. Supports multiple Drive URL formats.
        """
        link = str(link).strip()
        
        # Caso 1: Recursos en Google Drive (Soporta /d/ y open?id=)
        if 'drive.google.com' in link:
            file_id = None
            try:
                if '/d/' in link:
                    file_id = link.split('/d/')[1].split('/')[0]
                elif 'id=' in link:
                    file_id = link.split('id=')[1].split('&')[0]
                    
                if file_id:
                    # API de Miniaturas de Google Drive: Extrae la primera página en 500px de ancho
                    return f'https://drive.google.com/thumbnail?sz=w500&id={file_id}'
            except (IndexError, ValueError):
                pass
        
        # Caso 2: Videos de YouTube
        if 'youtube.com' in link or 'youtu.be' in link:
            try:
                if 'v=' in link:
                    video_id = link.split('v=')[1].split('&')[0]
                else:
                    video_id = link.split('/')[-1].split('?')[0]
                # Servidor de miniaturas oficial de YouTube
                return f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
            except IndexError:
                pass

        # Caso 3: Imagen por defecto según el tipo de archivo si no se cumple lo anterior
        # Usamos .capitalize() o .strip() para asegurar que coincida con las claves
        tipo_normalizado = str(tipo).strip().capitalize()
        
        dict_por_defecto = {
            'Libro': '/static/images/libro_default.png',
            'Tesis': '/static/images/tesis_default.png',
            'Guia': '/static/images/Guia_deafut.png',
            'Video': '/static/images/video_default.png',
            'Web': '/static/images/web_default.png'
        }
        return dict_por_defecto.get(tipo_normalizado, '/static/images/web_default.png')

    @staticmethod
    def _convertir_drive_url(url):
        """Convierte enlaces de Google Drive a formato de imagen."""
        if isinstance(url, str) and 'drive.google.com' in url and '/d/' in url:
            try:
                file_id = url.split('/d/')[1].split('/')[0]
                return f'https://drive.google.com/uc?export=view&id={file_id}'
            except IndexError:
                logger.warning(f"No se pudo convertir URL de Drive: {url}")
        return url
    
    # Propiedades y setters comunes
    @property
    def titulo(self): return self._titulo
    @titulo.setter
    def titulo(self, valor):
        valor = str(valor).strip()
        self._titulo = 'Sin titulo' if not valor or valor.lower() in ['none', 'nan', 'null', ''] else valor[:100]
    
    @property
    def autor(self): return self._autor
    @autor.setter
    def autor(self, valor):
        valor = str(valor).strip()
        self._autor = 'Anónimo' if not valor or valor.lower() in ['none', 'nan', 'null', ''] else valor[:100]
    
    @property
    def tipo(self): return self._tipo
    @tipo.setter
    def tipo(self, valor):
        val = str(valor).strip().capitalize()
        self._tipo = val if val in self.tipos_validos else 'Libro'
    
    @property
    def editorial(self): return self._editorial
    @editorial.setter
    def editorial(self, valor):
        valor = str(valor).strip()
        self._editorial = 'N/A' if not valor or valor.lower() in ['none', 'nan', 'null', ''] else valor[:100]
    
    @property
    def area(self): return self._area
    @area.setter
    def area(self, valor):
        valor = str(valor).strip()
        self._area = 'General' if not valor or valor.lower() in ['none', 'nan', 'null', ''] else valor[:100]
    
    @property
    def anio_publicacion(self): return self._anio_publicacion
    @anio_publicacion.setter
    def anio_publicacion(self, valor):
        valor_str = str(valor).strip()
        if valor_str in ['N/A', 'Año desconocido', '']:
            self._anio_publicacion = 'Año desconocido'
            return
        try:
            año = int(float(valor_str))
            if año in self.años_validos:
                self._anio_publicacion = str(año)
            else:
                logger.warning(f"Año '{año}' fuera de rango, asignando 'Año desconocido'.")
                self._anio_publicacion = 'Año desconocido'
        except (ValueError, TypeError):
            # Si contiene ":" es una duración de video, permitimos guardarla sin levantar alertas
            if ":" in valor_str:
                self._anio_publicacion = valor_str
            else:
                logger.warning(f"Valor de año inválido '{valor}', asignando 'Año desconocido'.")
                self._anio_publicacion = 'Año desconocido'
    
    @property
    def nivel(self): return self._nivel
    @nivel.setter
    def nivel(self, valor):
        valor = str(valor).strip()
        if valor in self.nivel_validos:
            self._nivel = valor
        else:
            logger.warning(f"Nivel '{valor}' no válido, asignando 'General'.")
            self._nivel = 'General'
    
    @property
    def link(self): return self._link
    @link.setter
    def link(self, valor):
        valor = str(valor).strip()
        parsed = urlparse(valor)
        if parsed.scheme in ['http', 'https'] and parsed.netloc:
            self._link = valor
        else:
            logger.warning(f"Link inválido '{valor}', asignando vacío.")
            self._link = ''
    
    @property
    def link_portada(self): return self._link_portada
    @link_portada.setter
    def link_portada(self, valor):
        if isinstance(valor, str) and valor.strip():
            valor_limpio = valor.strip()
            if valor_limpio.startswith(('http://', 'https://', 'data:image', '/static/')):
                self._link_portada = valor_limpio
            else:
                logger.warning(f"Formato de imagen no soportado: {valor_limpio[:50]}...")
                self._link_portada = ''
        else:
            self._link_portada = ''
    
    @property
    def descripcion(self): return self._descripcion
    @descripcion.setter
    def descripcion(self, valor):
        valor = str(valor).strip()
        self._descripcion = 'Sin descripción' if not valor or valor.lower() in ['none', 'nan', 'null', ''] else valor[:500]
    
    @property
    def id(self): return self._id
    
    # ✅ CORRECCIÓN: Añadido property y setter para 'estado'
    @property
    def estado(self): 
        return self._estado

    @estado.setter
    def estado(self, valor): 
        self._estado = str(valor).strip()

    def generar_tarjeta_html(self):
        raise NotImplementedError("Cada subclase debe implementar su propio diseño de tarjeta HTML")

    def to_dict(self):
        return {
            'ID': self.id, 'tipo': self.tipo, 'titulo': self.titulo, 'autor': self.autor,
            'editorial': self.editorial, 'area': self.area, 'nivel': self.nivel, 'link': self.link, 
            'link_portada': self.link_portada, 'anio_publicacion': self.anio_publicacion, 'descripcion': self.descripcion, 'estado': self._estado
        }

class Libro(RecursoAcademico):
    def __init__(self, titulo, autor, editorial, area, nivel, link, link_portada, anio_publicacion, descripcion, id_existente=None, estado='Pendiente'):
        # ✅ Ahora acepta 'estado' y lo pasa limpiamente a la clase base
        super().__init__(titulo, autor, editorial, area, nivel, link, link_portada, 'Libro', anio_publicacion, descripcion=descripcion, id_existente=id_existente, estado=estado)
    
    def to_dict(self):
        d = super().to_dict()
        d.update({'tipo': 'Libro', 'autor': self.autor, 'editorial': self.editorial, 'anio_publicacion': self.anio_publicacion})
        return d
        

                
class Tesis(RecursoAcademico):
    def __init__(self, titulo, autor, tutor, asesor_metodologico, area, nivel, link, link_portada, anio_publicacion, descripcion, id_existente=None, estado='Pendiente'):
        # ✅ Corrección aquí también para soportar el estado que venga del backend
        super().__init__(titulo, autor, 'N/A', area, nivel, link, link_portada, 'Tesis', anio_publicacion, descripcion, id_existente, estado=estado)
        self.tutor = tutor  
        self.asesor_metodologico = asesor_metodologico  
        
    def to_dict(self):
        d = super().to_dict()
        d.update({
            'tipo': 'Tesis',
            'autor': self.autor,
            'tutor': self.tutor,
            'asesor_metodologico': self.asesor_metodologico,
            'anio_publicacion': self.anio_publicacion
        })
        return d
        

                
class GuiaEstudio(RecursoAcademico):
    def __init__(self, titulo, autor, temas, area, nivel, link, anio_publicacion='Año desconocido', descripcion='Sin descripción', id_existente=None, link_portada='', estado='Pendiente'):
        # ✅ Pasamos el parámetro estado
        super().__init__(titulo, autor or 'Institucional', 'Material de Estudio', area, nivel, link, link_portada, 'Guia', anio_publicacion, descripcion, id_existente, estado=estado)
        self.temas = temas
        
    def to_dict(self):
        d = super().to_dict()
        d.update({
            'tipo': 'Guia',
            'autor': self.autor,
            'temas_clave': self.temas,
            'anio_publicacion': self.anio_publicacion,
            'estado': self._estado
        })
        return d
        

        
class VideoTutorial(RecursoAcademico):
    def __init__(self, titulo, duracion, area, nivel, link, anio_publicacion='Año desconocido', descripcion='Sin descripción', id_existente=None, autor='Multimedia', link_portada='', estado='Pendiente'):
        # ✅ Pasamos el parámetro estado
        super().__init__(titulo, autor, 'Internet', area, nivel, link, link_portada, 'Video', anio_publicacion, descripcion, id_existente, estado=estado)
        self.duracion = duracion
        
    def to_dict(self):
        d = super().to_dict()
        d.update({
            'tipo': 'Video',
            'duracion': self.duracion,
            'anio_publicacion': self.anio_publicacion,
            'estado': self._estado
        })
        return d
        


class PaginasWeb(RecursoAcademico):
    def __init__(self, titulo, plataforma, area, nivel, link, anio_publicacion='Año desconocido', descripcion='Sin descripción', id_existente=None, autor='Webmaster', link_portada='', estado='Pendiente'):
        # ✅ Pasamos el parámetro estado
        super().__init__(titulo, autor, 'Plataforma Digital', area, nivel, link, link_portada, 'Web', anio_publicacion, descripcion, id_existente, estado=estado)
        self.plataforma = plataforma
        
    def to_dict(self):
        d = super().to_dict()
        d.update({
            'tipo': 'Web',
            'plataforma': self.plataforma,
            'anio_publicacion': self.anio_publicacion,
            'estado': self._estado
        })
        return d
                     
class Biblioteca:
    def __init__(self, nombre):
        self.nombre = nombre
        self.lista_libros = []
    
    def agregar_recurso(self, recurso):
        if isinstance(recurso, RecursoAcademico):
            self.lista_libros.append(recurso)
        else:
            logger.warning(f"Intento de agregar recurso inválido: {type(recurso)}")
    
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
        """Recomienda recursos similares basados en autor, área y año."""
        similares = []
        similares.extend([r for r in self.buscar_por_autor(recurso.autor) if r != recurso])
        similares.extend([r for r in self.buscar_por_area(recurso.area) if r != recurso and r not in similares])
        try:
            anio = int(recurso.anio_publicacion)
            for offset in [-1, 0, 1]:
                similares.extend([r for r in self.buscar_por_anio(anio + offset) if r != recurso and r not in similares])
        except ValueError:
            pass
        return list(dict.fromkeys(similares))[:limite]
    
    def aprobado(self, recurso):
        if recurso._estado == 'Aprobado':
            return True
        return False
    
    def exportar_a_lista_dict(self):
        """Exporta la lista de libros a una lista de diccionarios para JSON."""
        return [libro.to_dict() for libro in self.lista_libros]
    
    def exportar_libros(self):
        """Exporta solo los libros (no tesis) a una lista de diccionarios."""
        return [libro.to_dict() for libro in self.lista_libros if not isinstance(libro, Tesis)]

    def exportar_tesis(self):
        """Exporta solo las tesis a una lista de diccionarios."""
        return [libro.to_dict() for libro in self.lista_libros if isinstance(libro, Tesis)]
    
    def exportar_repositorio(self):
        """Exporta los recursos que no son libros a una lista de diccionarios."""
        return [libro.to_dict() for libro in self.lista_libros if not isinstance(libro, Libro) and not isinstance(libro, Tesis)]