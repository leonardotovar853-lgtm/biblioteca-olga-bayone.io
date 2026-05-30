import pandas as pd
import gspread
from urllib.parse import urlparse
from modelos import RecursoAcademico, Biblioteca
import uuid
import random
import os
from sistemas_likes import obtener_likes_actualizados

def creador_objetos(df_limpio, biblioteca):
    """
    Convierte cada fila del DataFrame en un objeto RecursoAcademico
    """
    for _, fila in df_limpio.iterrows():
        nuevo_recurso = RecursoAcademico(
            titulo=fila.get('Titulo', ''),
            autor=fila.get('Autor', ''),
            editorial=fila.get('Editorial', ''),
            area=fila.get('Área de conocimiento', ''),
            nivel=fila.get('Nivel de Educación', ''),
            link=fila.get('Enlace del recurso', ''),
            link_portada=fila.get('Enlace de portada', ''),
            tipo=fila.get('Tipo de recurso', ''),
            anio_publicacion=fila.get('Año de publicación', ''),
            descripcion=fila.get('Descripción', ''),
            id_existente=fila.get('ID', None)
        )
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
        ruta_credenciales = r"C:\Users\NEW DELL\Documents\PROGRAMACIÓN\PROYECTO_BIBLIOTECA_DIGITAL\DATA\credenciales.json" # Cambia esto si tu archivo tiene otro nombre o ruta
        gc = gspread.service_account(filename=ruta_credenciales)
        sh = gc.open("Agregar Libro (Respuestas)")
        hoja_original = sh.get_worksheet(0)
        
        # ==========================================
        # 2. DESCARGA Y LIMPIEZA SEGURA
        # ==========================================
        df = pd.DataFrame(hoja_original.get_all_records())

        # BUSCAMOS Y BORRAMOS EL TIEMPO POR NOMBRE, NO POR POSICIÓN
        for col_basura in ['Marca temporal', 'Form_Responses', 'Timestamp']:
            if col_basura in df.columns:
                df = df.drop(columns=[col_basura])
                print(f"✅ Columna {col_basura} eliminada sin tocar el ID")
        
        def limpiar_id_desplazado(valor):
            texto = str(valor)
            # Si tiene "/" y ":" es una fecha (ej: 16/4/2026 21:37:37)
            if '/' in texto and ':' in texto:
                return '' # Lo vaciamos para que la Sección 2.5 genere un ID real
            return valor

        if 'ID' in df.columns:
            df['ID'] = df['ID'].apply(limpiar_id_desplazado)

        # Asegurar que ID sea la primera columna siempre
        if 'ID' not in df.columns:
            df.insert(0, 'ID', '')

        # Convertir nulos a texto vacío para que Python los vea
        df['ID'] = df['ID'].astype(str).replace(['nan', 'None', 'NaN', ''], '')
        # ==========================================
        # 2.5 GESTIÓN DE ID ÚNICO
        # ==========================================
        print("\n🆔 Verificando identificadores de recursos...")
        
        # Asegurar que la columna ID sea la primera desde el inicio
        if 'ID' not in df.columns:
            df.insert(0, 'ID', '')

        # Limpieza profunda de nulos para que Pandas no se confunda
        df['ID'] = df['ID'].astype(str).replace(['nan', 'None', 'NaN', 'null', ''], '')
        mask_vacio = (df['ID'].str.strip() == '')

        if mask_vacio.any():
            cantidad_nuevos = mask_vacio.sum()
            df.loc[mask_vacio, 'ID'] = [uuid.uuid4().hex[:8] for _ in range(cantidad_nuevos)]
            print(f"✅ Se generaron {cantidad_nuevos} IDs en memoria.")

            # --- ESCRITURA INMEDIATA ---
            print("💾 Sincronizando con Google Sheets...")
            
            # IMPORTANTE: Convertir TODO el DataFrame a strings y quitar nulos antes de subir
            # Esto evita que la API de Google rechace los datos
            df_subir = df.copy().fillna('')
            datos_resguardo = [df_subir.columns.values.tolist()] + df_subir.values.tolist()
            
            try:
                hoja_original.clear()
                # Usar una lista simple para el update suele ser más estable
                hoja_original.update('A1',datos_resguardo) 
                print("✨ ¡IDs guardados exitosamente en la base de datos!")
            except Exception as e:
                print(f"❌ Error al escribir en Sheets: {e}")
        # ==========================================
        # 3. VALIDACIÓN DE COLUMNAS REQUERIDAS
        # ==========================================
        columnas_requeridas = ['Titulo', 'Autor', 'Enlace del recurso']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            raise ValueError(f"Columnas requeridas faltantes: {columnas_faltantes}")
        
        biblioteca = Biblioteca('Biblioteca Olga Bayone')
        df = df.fillna('')
        
        # ==========================================
        # 4. LIMPIEZA DE DATOS
        # ==========================================
        print("\n🧹 Iniciando limpieza de datos...")
        
        # Limpiar espacios en blanco
        cols_para_limpiar = [c for c in df.columns if 'Enlace' not in c and 'link' not in c.lower()]
        for col in cols_para_limpiar:
            df[col] = df[col].astype(str).str.strip()
        
        # Eliminar basura (6+ repeticiones)
        filas_iniciales = len(df)
        for col in cols_para_limpiar:
            df = df[~df[col].str.contains(r'(.)\1{6,}', na=False, case=False)]
        
        filas_eliminadas = filas_iniciales - len(df)
        if filas_eliminadas > 0:
            print(f"🧹 Filas eliminadas por basura: {filas_eliminadas}")
        
        # ==========================================
        # 5. FILTRADO DE ENLACES VÁLIDOS
        # ==========================================
        col_enlace = 'Enlace del recurso'
        
        # Asegurar que sea string
        df[col_enlace] = df[col_enlace].astype(str)
        
        # Filtrar por http/https
        df = df[df[col_enlace].str.startswith(('http://', 'https://'), na=False)]
        
        # Validar con urlparse
        def es_url_valida(url):
            try:
                parsed = urlparse(str(url))
                return parsed.scheme in ['http', 'https'] and bool(parsed.netloc)
            except:
                return False
        
        df = df[df[col_enlace].apply(es_url_valida)]
        
        print(f"✅ Limpieza terminada. Filas válidas: {len(df)}")
        
        # ==========================================
        # 6. DETECCIÓN DE IMÁGENES BASE64
        # ==========================================
        col_portada = 'Enlace de portada'
        if col_portada in df.columns:
            df[col_portada] = df[col_portada].astype(str)
            
            # Identificar imágenes base64
            es_base64 = df[col_portada].str.startswith('data:image')
            cantidad_base64 = es_base64.sum()
            
            if cantidad_base64 > 0:
                print(f"\n🔴" + "="*60)
                print(f"🔴  ALERTA: {cantidad_base64} imágenes en formato BASE64")
                print("🔴" + "="*60)
                
                # Mostrar ejemplos
                for idx in df[es_base64].index[:3]:
                    fila = df.loc[idx]
                    print(f"   • {fila.get('Titulo', 'Sin título')}")
                    print(f"     Tamaño: {len(str(fila[col_portada]))} caracteres")
                    print(f"     Preview: {str(fila[col_portada])[:100]}...\n")
                
                print("🔴 Las imágenes funcionarán pero ocupan mucho espacio")
                print("🔴 Recomendación: Usar enlaces de Google Drive\n")

        # ==========================================
        # 6.7 GESTION DE LIKES
        # ==========================================
        
        obtener_likes_actualizados(df)
        
    
        # ==========================================
        # 7. ACTUALIZAR GOOGLE SHEETS
        # ==========================================
        if len(df) > 0:
            print("\n☁️ Actualizando Google Sheets...")
            
            # Limitar a 1000 filas por seguridad
            df_subir = df.head(1000)
            datos_formateados = [df_subir.columns.values.tolist()] + df_subir.values.tolist()
            
            # Limpiar y actualizar
            hoja_original.clear()
            hoja_original.update('A1', datos_formateados)
            
            print(f"✨ ¡Hoja actualizada con {len(df_subir)} filas!")
        else:
            print("⚠️ No hay datos válidos para actualizar.")
        
        # ==========================================
        # 8. CREACIÓN DE OBJETOS
        # ==========================================
        print("\n📚 Creando objetos RecursoAcademico...")
        creador_objetos(df, biblioteca)
        
        print(f"✅ Recursos creados: {len(biblioteca.lista_libros)}")
        
        # Mostrar resumen
        print("\n📊 RESUMEN FINAL:")
        print(f"   • Total recursos: {len(biblioteca.lista_libros)}")
        print(f"   • Libros: {sum(1 for r in biblioteca.lista_libros if not r.es_tesis)}")
        print(f"   • Tesis: {sum(1 for r in biblioteca.lista_libros if r.es_tesis)}")
        
        return biblioteca
    
    except gspread.exceptions.APIError as e:
        print(f"\n❌ Error de API de Google Sheets: {e}")
        print("   Posibles causas:")
        print("   • Credenciales inválidas")
        print("   • Sin conexión a internet")
        print("   • Límite de API excedido")
        return None
    
    except FileNotFoundError as e:
        print(f"\n❌ Archivo no encontrado: {e}")
        print("   Verificá que la ruta de credenciales sea correcta:")
        print("   C:\\Users\\NEW DELL\\Documents\\PROGRAMACIÓN\\PROYECTO_BIBLIOTECA_DIGITAL\\DATA\\credenciales.json")
        return None
    
    except ValueError as e:
        print(f"\n❌ Error de validación: {e}")
        import traceback
        traceback.print_exc()
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
        print(f"📊 Total recursos: {len(biblioteca.lista_libros)}")
        
        # Mostrar primeros 3 recursos como ejemplo
        if len(biblioteca.lista_libros) > 0:
            print("\n📋 Primeros recursos:")
            for i, recurso in enumerate(biblioteca.lista_libros[:3]):
                print(f"\n   {i+1}. {recurso.titulo}")
                print(f"      Autor: {recurso.autor}")
                print(f"      Año: {recurso.anio_publicacion}")
                print(f"      Nivel: {recurso.nivel}")
                print(f"      Tipo: {recurso.tipo}")
    else:
        print("\n❌ El proceso falló. Revisá los errores arriba.")