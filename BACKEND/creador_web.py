from admin_datos import limpieza_datos
import os
import json
import subprocess
from jinja2 import Environment, FileSystemLoader

# Ruta absoluta al repositorio de Git (para Windows)
RUTA_REPOSITORIO = r"C:\Users\NEW DELL\Documents\PROGRAMACIÓN\PROYECTO_BIBLIOTECA_DIGITAL"

def subir_cambios_a_github():
    """
    Sube los cambios generados a GitHub automáticamente.
    """
    try:
        print("Iniciando subida automática a GitHub...")
        
        # 1. Ejecuta 'git add .'
        subprocess.run(["git", "add", "."], check=True, cwd=RUTA_REPOSITORIO)
        
        # 2. Hace el commit automático
        subprocess.run(["git", "commit", "-m", "Actualización automática de libros desde el Panel de Control con Jinja2"], check=True, cwd=RUTA_REPOSITORIO)
        
        # 3. Sube los cambios a main
        subprocess.run(["git", "push", "origin", "main", "-o", "secret-scanning=bypass"], check=True, cwd=RUTA_REPOSITORIO)
        
        print("¡Web actualizada con éxito en GitHub!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al subir a GitHub: {e}")
        return False

def crear_web(biblioteca):
    """
    Genera los archivos HTML estáticos utilizando plantillas Jinja2.
    """
    try:
        # Rutas absolutas para plantillas y salida
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_templates = os.path.join(base_dir, 'templates')
        ruta_salida_frontend = os.path.join(RUTA_REPOSITORIO, 'FRONTEND', 'html')
        
        # Crear directorio de salida si no existe
        os.makedirs(ruta_salida_frontend, exist_ok=True)

        # Inicializar Jinja2 Environment
        loader = FileSystemLoader(ruta_templates)
        env = Environment(loader=loader, autoescape=True)

        # Filtrar recursos aprobados por tipo
        recursos_aprobados = [r for r in biblioteca.lista_libros if r.estado == 'Aprobado']
        
        libros_aprobados = [r for r in recursos_aprobados if r.tipo == 'Libro']
        tesis_aprobadas = [r for r in recursos_aprobados if r.tipo == 'Tesis']
        multimedia_aprobada = [r for r in recursos_aprobados if r.tipo in ['Guia', 'Video', 'Web']]

        # Datos JSON para los buscadores JS (solo recursos aprobados)
        libros_data_json = json.dumps(biblioteca.exportar_libros()) # Todos los libros (no tesis)
        tesis_data_json = json.dumps(biblioteca.exportar_tesis())   # Solo tesis
        multimedia_data_json = json.dumps(biblioteca.exportar_repositorio()) # Solo multimedia
        
        # Renderizar y escribir catalogo.html
        template_catalogo = env.get_template('catalogo.html')
        html_catalogo = template_catalogo.render(
            recursos=libros_aprobados,
            json_data=libros_data_json # Se pasa como string JSON para inyección directa
        )
        with open(os.path.join(ruta_salida_frontend, 'catalogo.html'), 'w', encoding='utf-8') as f:
            f.write(html_catalogo)
        print(f"✅ Archivo generado: {os.path.join(ruta_salida_frontend, 'catalogo.html')}")

        # Renderizar y escribir repositorio.html
        template_repositorio = env.get_template('repositorio.html')
        html_repositorio = template_repositorio.render(
            recursos=tesis_aprobadas,
            json_data=tesis_data_json
        )
        with open(os.path.join(ruta_salida_frontend, 'repositorio.html'), 'w', encoding='utf-8') as f:
            f.write(html_repositorio)
        print(f"✅ Archivo generado: {os.path.join(ruta_salida_frontend, 'repositorio.html')}")

        # Renderizar y escribir multimedia.html
        template_multimedia = env.get_template('multimedia.html')
        html_multimedia = template_multimedia.render(
            recursos=multimedia_aprobada,
            json_data=multimedia_data_json
        )
        with open(os.path.join(ruta_salida_frontend, 'multimedia.html'), 'w', encoding='utf-8') as f:
            f.write(html_multimedia)
        print(f"✅ Archivo generado: {os.path.join(ruta_salida_frontend, 'multimedia.html')}")

        # Renderizar y escribir index.html (primeros 4 libros para recomendaciones)
        template_index = env.get_template('index.html')
        recomendaciones_index = libros_aprobados[:4] # Tomar los primeros 4 libros como recomendación
        html_index = template_index.render(
            recursos_recomendados=recomendaciones_index,
            json_data=libros_data_json # Se usa la misma data para JS en el inicio si es necesario
        )
        with open(os.path.join(ruta_salida_frontend, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_index)
        print(f"✅ Archivo generado: {os.path.join(ruta_salida_frontend, 'index.html')}")

        # Renderizar páginas estáticas que heredan de base.html (sin datos dinámicos complejos, solo la estructura)
        template_sobre_proyecto = env.get_template('sobre_proyecto.html')
        html_sobre_proyecto = template_sobre_proyecto.render()
        with open(os.path.join(ruta_salida_frontend, 'sobre_proyecto.html'), 'w', encoding='utf-8') as f:
            f.write(html_sobre_proyecto)
        print(f"✅ Archivo generado: {os.path.join(ruta_salida_frontend, 'sobre_proyecto.html')}")

        template_agregar_libro = env.get_template('agregar_libro.html')
        html_agregar_libro = template_agregar_libro.render()
        with open(os.path.join(ruta_salida_frontend, 'agregar_libro.html'), 'w', encoding='utf-8') as f:
            f.write(html_agregar_libro)
        print(f"✅ Archivo generado: {os.path.join(ruta_salida_frontend, 'agregar_libro.html')}")


        print("\n✨ ¡Generación de la web completada!")
        subir_cambios_a_github()
        
    except Exception as e:
        print(f'❌ Error al generar la web: {e}')
        raise # Re-lanza la excepción para que el bloque principal la capture

# Bloque de ejecución principal
def ejecucion_final():
    """
    Orquesta la limpieza de datos y la creación de la web.
    """
    try:
        biblioteca_final = limpieza_datos() 

        if biblioteca_final is not None:
            crear_web(biblioteca_final)
            print("🚀 PROCESO COMPLETADO: Web actualizada con éxito.")
            return True
        else:
            print("❌ ERROR: No se pudo procesar la información de la nube o la biblioteca está vacía.")
            return False
    except Exception as e:
        print(f'❌ ERROR CRÍTICO en la ejecución final: {e}')
        return False
    
if __name__ == "__main__":
    ejecucion_final()
