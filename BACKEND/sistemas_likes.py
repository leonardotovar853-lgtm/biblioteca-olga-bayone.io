import requests # Importamos requests para la url

def obtener_likes_actualizados(df): 
    
    url_firebase = "https://biblioteca-olga-bayone-default-rtdb.firebaseio.com/.json"
    
    try:
        print("Conectando con Firebase...")
        respuesta = requests.get(url_firebase)
        
        if respuesta.status_code == 200:
            likes_nube = respuesta.json() # Obteniendo diccionario en formato json de los likes
            
            if likes_nube:
                # Mapeamos los likes al DataFrame usando la columna 'ID'
                # Si el ID no existe en Firebase, pone 0 (fillna)
                df['Likes'] = df['ID'].map(likes_nube).fillna(0).astype(int)
                print(f"[OK] Se sincronizaron likes para {len(likes_nube)} libros.")
            else:
                print("[INFO] No hay likes registrados en la nube todavía.")
                df['Likes'] = 0
        
        else:
            print(f"[ERROR] Error al conectar con Firebase: {respuesta.status_code}")
            
    except Exception as e:
        print(f"[WARN] Ocurrió un error en la sincronización: {e}")
        
    return df
                
