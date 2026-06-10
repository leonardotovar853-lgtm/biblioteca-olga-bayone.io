import pandas as pd
import gspread
from urllib.parse import urlparse
from modelos import Biblioteca, Libro, Tesis, GuiaEstudio, VideoTutorial, PaginasWeb
import uuid
import random
import os
from sistemas_likes import obtener_likes_actualizados

def creador_objetos(df_limpio, biblioteca):
    """
    Convierte cada fila del DataFrame en un objeto RecursoAcademico
    """
    for _, fila in df_limpio.iterrows():
        tipo = str(fila.get('Tipo de Recurso', 'Libro')).strip().lower() # Corregido a 'Tipo de Recurso' coincidiendo con las columnas consolidada
        
        id_existente = fila.get('ID', None)
        titulo = fila.get('Titulo', '')
        autor = fila.get('Autor', '')
        area = fila.get('Área de Conocimiento', '')
        nivel = fila.get('Nivel de Educación', '')
        link = fila.get('Enlace del recurso', '') # Corregido al nombre limpio de columna
        link_portada = fila.get('Enlace de Portada', '')
        descripcion = fila.get('Descripción', '')
        anio = fila.get('Año de publicacion', 'Año desconocido') # Corregido al nombre limpio de columna
        
        # Verificacion de tipo de recurso y creacion de objeto respectivo
        if tipo == 'libro':
            editorial = fila.get('Editorial', '')
            nuevo_recurso = Libro(titulo, autor, editorial, area, nivel, link, link_portada, anio, descripcion, id_existente)
        elif tipo == 'tesis':
            tutor = fila.get('Tutor') or 'Sin Tutor'
            asesor_metodologico = fila.get('Asesor Metodologico') or 'Sin Asesor'
            nuevo_recurso = Tesis(
                titulo,
                autor,
                tutor,
                asesor_metodologico,
                area,
                nivel,
                link,
                link_portada,
                anio,
                descripcion,
                id_existente
            )
        elif tipo == 'guia':
            temas = fila.get('Temas Clave') or 'General'
            nuevo_recurso = GuiaEstudio(titulo, autor, temas, area, nivel, link, anio, descripcion, id_existente)
        elif tipo == 'video':
            duracion = fila.get('Duración') or '00:00'
            nuevo_recurso = VideoTutorial(titulo, duracion, area, nivel, link, anio, descripcion, id_existente)
        elif tipo == 'web':
            plataforma = fila.get('Plataforma') or 'Internet'
            nuevo_recurso = PaginasWeb(titulo, plataforma, area, nivel, link, anio, descripcion, id_existente)
        else:
            editorial = fila.get('Editorial', 'N/A')
            nuevo_recurso = Libro(titulo, autor, editorial, area, nivel, link, link_portada, anio, descripcion, id_existente)

        biblioteca.agregar_recurso(nuevo_recurso)

def limpieza_datos():
    """
    Función principal que orquesta todo el proceso:
    1. Conecta con Google Sheets
    2. Descarga y limpia datos
    3. Actualiza la hoja
    4. Crea objetos RecursoAcademico
    5. Retorna biblioteca con todos los recursos
    """
    try:
        print('🌐 Conectando con Google Sheets...')
        
        # ==========================================
        # 1. CONEXIÓN A GOOGLE SHEETS
        # ==========================================
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
                for col in df.columns:
                    if str(col).strip().lower().startswith('año'):
                        df = df.rename(columns={col: 'Año de publicacion'})    
                
                # Homologar nombres de columnas de los formularios
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
                    elif 'área de conocimiento' in col_limpia or 'area de conocimiento' in col_limpia or 'área de conocimiento' in col_limpia:
                        columnas_nuevas[col] = 'Área de Conocimiento'
                    elif 'nivel de educación' in col_limpia or 'nivel de educacion' in col_limpia:
                        columnas_nuevas[col] = 'Nivel de Educación'
                    elif 'enlace del recurso' in col_limpia or 'link del recurso' in col_limpia:
                        columnas_nuevas[col] = 'Enlace del recurso'
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
                        columnas_nuevas[col] = col  # Mantener igual si no aplica a ninguna regla
                
                # Aplicamos el renombrado robusto
                df = df.rename(columns=columnas_nuevas)
                
                df['Tipo de Recurso'] = recurso_tipo
                lista_df.append(df)
                
            except gspread.exceptions.WorksheetNotFound:
                print(f"⚠️ Hoja '{form_name}' no encontrada. Se omitirá.")
        
        if not lista_df:
            print("⚠️ No se encontraron datos en ningún formulario.")
            return None
        
        Df_final = pd.concat(lista_df, ignore_index=True, sort=False)
        
        columnas = [
            'ID', 'Tipo de Recurso', 'Titulo', 'Autor', 'Editorial', 'Tutor', 'Asesor Metodologico',
            'Área de Conocimiento', 'Nivel de Educación', 'Enlace del recurso', 
            'Enlace de Portada', 'Año de publicacion', 'Descripción', 'Temas Clave', 
            'Duración', 'Plataforma', 'Likes', 'Validación'
        ]
        
        # ==========================================
        # 2. SEPARACIÓN Y RESCATE DE IDS EXISTENTES
        # ==========================================
        Df_final = Df_final.reindex(columns=columnas)
        
        print("\n🔍 Buscando registros existentes en 'BD_General' para conservar IDs...")
        dict_ids_viejos = {}
        try:
            hoja_destino = sh.worksheet('BD_General')
            datos_generales = hoja_destino.get_all_records()
            if datos_generales:
                df_existente = pd.DataFrame(datos_generales)
                # Creamos una clave basada en (Titulo, Autor) para recordar su ID real
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

        # ==========================================
        # 2.5 ASIGNACIÓN INTELIGENTE DE IDENTIFICADORES
        # ==========================================
        print("🆔 Verificando identificadores estables de recursos...")
        
        ids_finales = []
        nuevos_contados = 0
        
        for _, fila in Df_final.iterrows():
            # Limpiamos los datos de la fila actual para comparar
            titulo_actual = str(fila.get('Titulo', '')).strip().lower()
            autor_actual = str(fila.get('Autor', '')).strip().lower()
            llave_actual = (titulo_actual, autor_actual)
            
            id_formulario = str(fila.get('ID', '')).strip()
            # Validar que no se haya colado una marca temporal en el ID
            if '/' in id_formulario and ':' in id_formulario:
                id_formulario = ''

            # 1. ¿Ya existía en la base de datos BD_General? (Mantenemos ID viejo)
            if llave_actual in dict_ids_viejos:
                ids_finales.append(dict_ids_viejos[llave_actual])
            # 2. ¿El formulario individual ya venía con un ID asignado válido?
            elif id_formulario != '' and id_formulario.lower() not in ['nan', 'none', 'null']:
                ids_finales.append(id_formulario)
            # 3. Es un recurso completamente nuevo ingresado
            else:
                ids_finales.append(uuid.uuid4().hex[:8])
                nuevos_contados += 1
                
        # Inyectamos la lista de IDs estables al DataFrame consolidado
        Df_final['ID'] = ids_finales
        print(f"✅ Identificación lista. Conservados: {len(ids_finales) - nuevos_contados} | Nuevos generados: {nuevos_contados}")

        # Rellenar vacíos para evitar celdas rotas antes de validar
        Df_final = Df_final.fillna('N/A')
        
        
        Df_final['Año de publicacion'] = Df_final['Año de publicacion'].astype(str).replace(['N/A', 'n/a', 'NaN', 'nan'], 'Año desconocido')
        
        # ==========================================
        # 3. VALIDACIÓN DE COLUMNAS REQUERIDAS
        # ==========================================
        columnas_requeridas = ['Titulo', 'Autor', 'Enlace del recurso']
        columnas_faltantes = [col for col in columnas_requeridas if col not in Df_final.columns]
        
        if columnas_faltantes:
            raise ValueError(f"Columnas requeridas faltantes: {columnas_faltantes}")
        
        biblioteca = Biblioteca('Biblioteca Olga Bayone')
        
        # ==========================================
        # 4. LIMPIEZA DE DATOS (Strings y Basura)
        # ==========================================
        print("\n🧹 Iniciando limpieza de strings y caracteres repetidos...")
        cols_para_limpiar = [c for c in Df_final.columns if 'Enlace' not in c and 'link' not in c.lower() and c != 'ID']
        for col in cols_para_limpiar:
            Df_final[col] = Df_final[col].astype(str).str.strip()
        
        # Eliminar spam (6+ repeticiones de un mismo caracter)
        filas_iniciales = len(Df_final)
        for col in cols_para_limpiar:
            Df_final = Df_final[~Df_final[col].str.contains(r'(.)\1{6,}', na=False, case=False)]
        
        filas_eliminadas = filas_iniciales - len(Df_final)
        if filas_eliminadas > 0:
            print(f"🧹 Filas eliminadas por spam/basura: {filas_eliminadas}")
        
        # ==========================================
        # 5. FILTRADO DE ENLACES VÁLIDOS
        # ==========================================
        col_enlace = 'Enlace del recurso'
        Df_final[col_enlace] = Df_final[col_enlace].astype(str).str.strip()
        
        # Filtrar enlaces con esquema web correcto
        Df_final = Df_final[Df_final[col_enlace].str.startswith(('http://', 'https://'), na=False)]
        
        def es_url_valida(url):
            try:
                parsed = urlparse(str(url))
                return parsed.scheme in ['http', 'https'] and bool(parsed.netloc)
            except:
                return False
        
        Df_final = Df_final[Df_final[col_enlace].apply(es_url_valida)]
        print(f"✅ Enlaces validados. Filas limpias finales: {len(Df_final)}")
        
        # ==========================================
        # 6. DETECCIÓN DE IMÁGENES BASE64
        # ==========================================
        col_portada = 'Enlace de Portada'
        if col_portada in Df_final.columns:
            Df_final[col_portada] = Df_final[col_portada].astype(str).str.strip()
            es_base64 = Df_final[col_portada].str.startswith('data:image')
            cantidad_base64 = es_base64.sum()
            
            if cantidad_base64 > 0:
                print(f"\n🔴" + "="*60)
                print(f"🔴  ALERTA: {cantidad_base64} imágenes en formato BASE64")
                print("🔴" + "="*60)
                for idx in Df_final[es_base64].index[:3]:
                    fila = Df_final.loc[idx]
                    print(f"   • {fila.get('Titulo', 'Sin título')}")
                    print(f"     Tamaño: {len(str(fila[col_portada]))} caracteres")
                print("🔴 Recomendación: Reemplazar por URLs tradicionales para evitar saturar la hoja.\n")

        # ==========================================
        # 6.7 GESTION DE LIKES
        # ==========================================
        #obtener_likes_actualizados(Df_final)
        
        # ==========================================
        # 7. ACTUALIZAR GOOGLE SHEETS (Escritura Única)
        # ==========================================
        if len(Df_final) > 0:
            print("\n☁️ Sincronizando y guardando datos en 'BD_General'...")
            
            # Limitar a 1000 filas por seguridad y formatear para gspread
            Df_final_subir = Df_final.head(1000).copy().fillna('N/A')
            datos_formateados = [Df_final_subir.columns.values.tolist()] + Df_final_subir.values.tolist()
            
            # Ejecutamos una sola limpieza y una sola subida
            hoja_destino.clear()
            hoja_destino.update('A1', datos_formateados)
            print(f"✨ ¡Base de Datos general consolidada con {len(Df_final_subir)} filas!")
        else:
            print("⚠️ No hay datos válidos tras el filtrado para actualizar la hoja.")
        
        # ==========================================
        # 8. CREACIÓN DE OBJETOS EN MEMORIA
        # ==========================================
        print("\n📚 Instanciando objetos de la estructura de datos...")
        creador_objetos(Df_final, biblioteca)
        
        # Mostrar resumen final alineado a Catálogo vs Repositorio
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
    
    except gspread.exceptions.APIError as e:
        print(f"\n❌ Error de API de Google Sheets: {e}")
        return None
    except FileNotFoundError as e:
        print(f"\n❌ Archivo de credenciales no encontrado. Verifique la ruta del JSON.")
        return None
    except ValueError as e:
        print(f"\n❌ Error de validación: {e}")
        return None
    except Exception as e:
        print(f"\n❌ Error crítico inesperado: {e}")
        import traceback
        traceback.print_exc()
        return None

# ==========================================
# EJECUCIÓN DE PRUEBA
# ==========================================
if __name__ == '__main__':
    print("="*60)
    print("🚀 INICIANDO PROCESO DE LIMPIEZA DE DATOS")
    print("="*60)
    
    biblioteca = limpieza_datos()
    
    if biblioteca:
        print("\n" + "="*60)
        print("✅ PROCESO COMPLETADO CON ÉXITO")
        print("="*60)
        print(f"\n📚 Biblioteca: {biblioteca.nombre}")
        
        if len(biblioteca.lista_libros) > 0:
            print("\n📋 Muestra de primeros recursos creados:")
            for i, recurso in enumerate(biblioteca.lista_libros[:3]):
                print(f"\n   {i+1}. {recurso.titulo}")
                print(f"      Autor: {recurso.autor}")
                print(f"      Año: {recurso.anio_publicacion}")
                print(f"      Nivel: {recurso.nivel}")
                print(f"      Tipo: {recurso.tipo}")
    else:
        print("\n❌ El proceso falló. Revisá los errores arriba.")