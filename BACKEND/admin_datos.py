import pandas as pd
import gspread
from urllib.parse import urlparse
from modelos import RecursoAcademico, Biblioteca, Libro, Tesis, GuiaEstudio, VideoTutorial, PaginasWeb
import uuid
import random
import os
from sistemas_likes import obtener_likes_actualizados

def creador_objetos(df_limpio, biblioteca):
    """
    Convierte cada fila del DataFrame en un objeto RecursoAcademico.
    CORREGIDO: Se usan argumentos por nombre (kwargs) para garantizar que 
    el año y la portada caigan en sus variables correspondientes sin importar el orden del __init__.
    """
    for _, fila in df_limpio.iterrows():
        tipo = str(fila.get('Tipo de Recurso', 'Libro')).strip().lower() 
        
        id_existente = fila.get('ID', None)
        titulo = fila.get('Titulo', '')
        autor = fila.get('Autor', '')
        area = fila.get('Área de Conocimiento', '')
        nivel = fila.get('Nivel de Educación', '')
        link = fila.get('Enlace del recurso', '') 
        link_portada = str(fila.get('Enlace de Portada', '')).strip()
        descripcion = fila.get('Descripción', '')
        anio = fila.get('Año de publicacion', 'Año desconocido') 
        
        if tipo == 'libro':
            editorial = fila.get('Editorial', '')
            nuevo_recurso = Libro(
                titulo, autor, editorial, area, nivel, link, link_portada, 
                anio_publicacion=anio, descripcion=descripcion, id_existente=id_existente
            )
            
        elif tipo == 'tesis':
            tutor = fila.get('Tutor') or 'Sin Tutor'
            asesor_metodologico = fila.get('Asesor Metodologico') or 'Sin Asesor'
            nuevo_recurso = Tesis(
                titulo, autor, tutor, asesor_metodologico, area, nivel, link, link_portada, 
                anio_publicacion=anio, descripcion=descripcion, id_existente=id_existente
            )
            
        elif tipo == 'guia':
            temas = fila.get('Temas Clave') or 'General'
            # 🌟 Ajustado explícitamente al formato de tu modelos.py
            nuevo_recurso = GuiaEstudio(
                titulo=titulo, autor=autor, temas=temas, area=area, nivel=nivel, link=link,
                anio_publicacion=anio, descripcion=descripcion, id_existente=id_existente, link_portada=link_portada
            )
            
        elif tipo == 'video':
            duracion = fila.get('Duración') or '00:00'
            # 🌟 Ajustado explícitamente al formato de tu modelos.py
            nuevo_recurso = VideoTutorial(
                titulo=titulo, duracion=duracion, area=area, nivel=nivel, link=link,
                anio_publicacion=anio, descripcion=descripcion, id_existente=id_existente, link_portada=link_portada
            )
            
        elif tipo == 'web':
            plataforma = fila.get('Plataforma') or 'Internet'
            nuevo_recurso = PaginasWeb(
                titulo=titulo, plataforma=plataforma, area=area, nivel=nivel, link=link,
                anio_publicacion=anio, descripcion=descripcion, id_existente=id_existente, link_portada=link_portada
            )
            
        else:
            editorial = fila.get('Editorial', 'N/A')
            nuevo_recurso = Libro(
                titulo, autor, editorial, area, nivel, link, link_portada, 
                anio_publicacion=anio, descripcion=descripcion, id_existente=id_existente
            )

        biblioteca.agregar_recurso(nuevo_recurso)
        
def limpieza_datos():
    """
    Función principal que orquesta todo el proceso
    """
    try:
        print('🌐 Conectando con Google Sheets...')
        
        ruta_credenciales = r"C:\Users\NEW DELL\Documents\PROGRAMACIÓN\PROYECTO_BIBLIOTECA_DIGITAL\DATA\credenciales.json"
        gc = gspread.service_account(filename=ruta_credenciales)
        sh = gc.open("Agregar Libro (Respuestas)")
        
        forms = {
            'Form_Libros': 'Libro',
            'Form_Tesis': 'Tesis',
            'Form_Guias': 'Guia',
            'Form_Videos': 'Video',
            'Form_Web': 'Web'
        }
        
        lista_df = []
        
        for form_name, recurso_tipo in forms.items():
            try:
                hoja = sh.worksheet(form_name)
                datos = hoja.get_all_records()
                
                if not datos:
                    print(f"⚠️ La hoja '{form_name}' está vacía. Se omitirá.")
                    continue
                
                df = pd.DataFrame(datos)
                
                # Quitar columnas innecesarias
                for col_basura in ['Marca temporal', 'Form_Responses', 'Timestamp']:
                    if col_basura in df.columns:
                        df = df.drop(columns=[col_basura])
                
                # Homologar nombres de columnas
                columnas_nuevas = {}
                for col in df.columns:
                    col_limpia = str(col).strip().lower()
                    
                    if col_limpia.startswith(('año', 'ano')):
                        columnas_nuevas[col] = 'Año de publicacion'
                    elif col_limpia in ['título', 'titulo']:
                        columnas_nuevas[col] = 'Titulo'
                    elif col_limpia in ['autor', 'autor(es)']:
                        columnas_nuevas[col] = 'Autor'
                    elif col_limpia == 'id':
                        columnas_nuevas[col] = 'ID'
                    elif col_limpia == 'editorial':
                        columnas_nuevas[col] = 'Editorial'
                    elif col_limpia == 'tutor':
                        columnas_nuevas[col] = 'Tutor'
                    elif 'asesor' in col_limpia or 'metodolo' in col_limpia:
                        columnas_nuevas[col] = 'Asesor Metodologico'
                    elif 'área de conocimiento' in col_limpia or 'area de conocimiento' in col_limpia:
                        columnas_nuevas[col] = 'Área de Conocimiento'
                    elif 'nivel de educación' in col_limpia or 'nivel de educacion' in col_limpia:
                        columnas_nuevas[col] = 'Nivel de Educación'
                    elif 'enlace del recurso' in col_limpia or 'link del recurso' in col_limpia:
                        columnas_nuevas[col] = 'Enlace del recurso'
                    elif 'archivo local drive' in col_limpia or 'archivo local' in col_limpia:
                        columnas_nuevas[col] = 'Archivo Local Drive'
                    elif 'portada' in col_limpia:
                        columnas_nuevas[col] = 'Enlace de Portada'
                    elif 'descrip' in col_limpia:
                        columnas_nuevas[col] = 'Descripción'
                    elif 'temas' in col_limpia:
                        columnas_nuevas[col] = 'Temas Clave'
                    elif 'durac' in col_limpia:
                        columnas_nuevas[col] = 'Duración'
                    elif 'plataforma' in col_limpia:
                        columnas_nuevas[col] = 'Plataforma'
                    else:
                        columnas_nuevas[col] = col 
                
                df = df.rename(columns=columnas_nuevas)
                
                # Consolidación del enlace del recurso o archivo local
                if 'Archivo Local Drive' in df.columns:
                    if 'Enlace del recurso' in df.columns:
                        df['Enlace del recurso'] = df['Enlace del recurso'].replace('', None).combine_first(df['Archivo Local Drive'].replace('', None)).fillna('')
                    else:
                        df['Enlace del recurso'] = df['Archivo Local Drive']
                    df = df.drop(columns=['Archivo Local Drive'])
                # Eliminar columnas duplicadas que puedan haber surgido por renombrados o formatos inconsistentes
                df = df.loc[:, ~df.columns.duplicated()]
                df['Tipo de Recurso'] = recurso_tipo
                lista_df.append(df)
                
            except gspread.exceptions.WorksheetNotFound:
                print(f"⚠️ Hoja '{form_name}' no encontrada. Se omitirá.")
        
        if not lista_df:
            print("⚠️ No se encontraron datos en ningún formulario.")
            return None
        
        Df_final = pd.concat(lista_df, ignore_index=True, sort=False)
        Df_final = Df_final.loc[:, ~Df_final.columns.duplicated()]
        
        columnas = [
            'ID', 'Tipo de Recurso', 'Titulo', 'Autor', 'Editorial', 'Tutor', 'Asesor Metodologico',
            'Área de Conocimiento', 'Nivel de Educación', 'Enlace del recurso', 
            'Enlace de Portada', 'Año de publicacion', 'Descripción', 'Temas Clave', 
            'Duración', 'Plataforma', 'Likes', 'Validación'
        ]
        
        Df_final = Df_final.reindex(columns=columnas)
        Df_final = Df_final.fillna('N/A')
        Df_final['Año de publicacion'] = Df_final['Año de publicacion'].astype(str).replace(['N/A', 'n/a', 'NaN', 'nan'], 'Año desconocido')
        
        print("\n🔍 Buscando registros existentes en 'BD_General' para conservar IDs...")
        dict_ids_viejos = {}
        try:
            hoja_destino = sh.worksheet('BD_General')
            datos_generales = hoja_destino.get_all_records()
            if datos_generales:
                df_existente = pd.DataFrame(datos_generales)
                for _, fila_ext in df_existente.iterrows():
                    titulo_ext = str(fila_ext.get('Titulo', '')).strip().lower()
                    autor_ext = str(fila_ext.get('Autor', '')).strip().lower()
                    id_ext = str(fila_ext.get('ID', '')).strip()
                    
                    if titulo_ext and autor_ext and id_ext and '/' not in id_ext:
                        dict_ids_viejos[(titulo_ext, autor_ext)] = id_ext
                print(f"📋 Se rescataron {len(dict_ids_viejos)} IDs guardados previamente.")
        except gspread.exceptions.WorksheetNotFound:
            print("✨ No se encontró 'BD_General'. Se creará automáticamente al final.")
            hoja_destino = sh.add_worksheet(title="BD_General", rows="1000", cols="20")

        print("🆔 Verificando identificadores estables de recursos...")
        ids_finales = []
        nuevos_contados = 0
        
        for _, fila in Df_final.iterrows():
            titulo_actual = str(fila.get('Titulo', '')).strip().lower()
            autor_actual = str(fila.get('Autor', '')).strip().lower()
            llave_actual = (titulo_actual, autor_actual)
            
            id_formulario = str(fila.get('ID', '')).strip()
            if '/' in id_formulario and ':' in id_formulario:
                id_formulario = ''

            if llave_actual in dict_ids_viejos:
                ids_finales.append(dict_ids_viejos[llave_actual])
            elif id_formulario != '' and id_formulario.lower() not in ['nan', 'none', 'null', 'n/a']:
                ids_finales.append(id_formulario)
            else:
                ids_finales.append(uuid.uuid4().hex[:8])
                nuevos_contados += 1
                
        Df_final['ID'] = ids_finales
        print(f"✅ Identificación lista. Conservados: {len(ids_finales) - nuevos_contados} | Nuevos generados: {nuevos_contados}")

        print("\n🧹 Iniciando limpieza de strings y caracteres repetidos...")
        cols_para_limpiar = [c for c in Df_final.columns if 'Enlace' not in c and 'link' not in c.lower() and c != 'ID']
        for col in cols_para_limpiar:
            Df_final[col] = Df_final[col].astype(str).str.strip()
        
        # Eliminar spam
        filas_iniciales = len(Df_final)
        for col in cols_para_limpiar:
            Df_final = Df_final[~Df_final[col].str.contains(r'(.)\1{6,}', na=False, case=False)]
        
        filas_eliminadas = filas_iniciales - len(Df_final)
        if filas_eliminadas > 0:
            print(f"🧹 Filas eliminadas por spam/basura: {filas_eliminadas}")
        
        def es_url_valida(url):
            try:
                parsed = urlparse(str(url).strip())
                return parsed.scheme in ['http', 'https'] and bool(parsed.netloc)
            except:
                return False
        # =========================================================================
        # 🌟 NUEVA SECCIÓN: VERIFICACIÓN Y GENERACIÓN AUTOMÁTICA EN EL DATAFRAME
        # =========================================================================
        print("🖼️ Verificando y generando portadas automáticas faltantes...")
        portadas_actualizadas = []

        for _, fila in Df_final.iterrows():
            link_recurso = str(fila.get('Enlace del recurso', '')).strip()
            portada_actual = str(fila.get('Enlace de Portada', '')).strip()
            tipo_recurso = str(fila.get('Tipo de Recurso', 'Libro')).strip().capitalize()
            
            # Si no hay portada, es N/A, o contiene un formato incorrecto (como un Base64 dañado)
            if not portada_actual or portada_actual in ['N/A', 'n/a', 'NaN', 'nan', ''] or not portada_actual.startswith(('http://', 'https://')):
                # Invocamos la generación inteligente ANTES de subir el DataFrame
                portada_nueva = RecursoAcademico._generar_portada_automatica(link_recurso, tipo_recurso)
                portadas_actualizadas.append(portada_nueva)
            else:
                # Si el usuario metió una URL manual válida en el formulario, se conserva
                portadas_actualizadas.append(portada_actual)
                
        Df_final['Enlace de Portada'] = portadas_actualizadas
        # =========================================================================

        print("🔍 Validando enlaces unificados de recursos...")
        Df_final = Df_final[Df_final['Enlace del recurso'].apply(es_url_valida)]
        print(f"✅ Enlaces validados. Filas limpias finales: {len(Df_final)}")

        if len(Df_final) > 0:
            print("\n☁️ Sincronizando y guardando datos en 'BD_General'...")
            Df_final_subir = Df_final.head(1000).copy().fillna('N/A')
            datos_formateados = [Df_final_subir.columns.values.tolist()] + Df_final_subir.values.tolist()
            
            hoja_destino.clear()
            # CORREGIDO: Argumentos en orden correcto para evitar el DeprecationWarning
            hoja_destino.update(values=datos_formateados, range_name='A1')
            print(f"✨ ¡Base de Datos general consolidada con {len(Df_final_subir)} filas!")
        else:
            print("⚠️ No hay datos válidos tras el filtrado para actualizar la hoja.")
        
        print("\n📚 Instanciando objetos de la estructura de datos...")
        biblioteca = Biblioteca('Biblioteca Olga Bayone')
        creador_objetos(Df_final, biblioteca)
        
        # 🌟 REINCORPORADO: Resumen estadístico detallado de recursos en consola
        print("\n📊 RESUMEN DE CLASIFICACIÓN FINAL:")
        print(f"   • Total recursos en memoria: {len(biblioteca.lista_libros)}")
        print("-" * 40)
        print(f"   📚 [CATÁLOGO] Libros estrictos: {sum(1 for r in biblioteca.lista_libros if type(r) == Libro)}")
        print(f"   📂 [REPOSITORIO] Tesis:        {sum(1 for r in biblioteca.lista_libros if isinstance(r, Tesis))}")
        print(f"   📂 [REPOSITORIO] Guías:        {sum(1 for r in biblioteca.lista_libros if isinstance(r, GuiaEstudio))}")
        print(f"   📂 [REPOSITORIO] Videos:       {sum(1 for r in biblioteca.lista_libros if isinstance(r, VideoTutorial))}")
        print(f"   📂 [REPOSITORIO] Webs:         {sum(1 for r in biblioteca.lista_libros if isinstance(r, PaginasWeb))}")
        print("-" * 40)
        
        return biblioteca
    
    except Exception as e:
        print(f"\n❌ Error crítico inesperado: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    print("="*60)
    print("🚀 INICIANDO PROCESO DE LIMPIEZA DE DATOS")
    print("="*60)
    biblioteca = limpieza_datos()