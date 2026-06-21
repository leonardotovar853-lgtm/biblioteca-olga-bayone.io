from creador_web import ejecucion_final
import tkinter as tk 
from tkinter import messagebox, ttk, filedialog
import webbrowser
import os
import csv
from datetime import datetime

# NOTA: Simulación de gspread. Aquí debes importar tu objeto 'sheet' real.
# Ejemplo: from tu_modulo_conexion import sheet

from creador_web import ejecucion_final
import tkinter as tk 
from tkinter import messagebox, ttk, filedialog
import webbrowser
import os
import csv
from datetime import datetime
import gspread

# ==========================================
# CONEXIÓN GLOBAL CON TU BD GENERAL (gspread)
# ==========================================
try:
    ruta_credenciales = r"C:\Users\NEW DELL\Documents\PROGRAMACIÓN\PROYECTO_BIBLIOTECA_DIGITAL\DATA\credenciales.json"
    
    if os.path.exists(ruta_credenciales):
        gc = gspread.service_account(filename=ruta_credenciales)
        sh = gc.open("Agregar Libro (Respuestas)")
        sheet = sh.worksheet('BD_General')
    else:
        print("Advertencia: El archivo credenciales.json no existe en la ruta especificada.")
        sheet = None
except Exception as e:
    print(f"Error crítico al conectar con Google Sheets: {e}")
    sheet = None  

def abrir_panel():  # Función Para Abrir el Panel de Control
    root = tk.Tk()
    root.geometry("750x650")  
    root.config(background='#f1f5f9')
    root.title('Panel de Control - Biblioteca Digital Olga Bayone')
    root.resizable(True, True)
    root.maxsize(900, 800)
    root.minsize(650, 550)

    try:
        root.iconbitmap(r'C:\Users\NEW DELL\Documents\PROGRAMACIÓN\PROYECTO_BIBLIOTECA_DIGITAL\FRONTEND\logo_olga_bayone.ico')
    except:
        pass

    # ==========================================
    # LÓGICA DE CONTROL (PROCESAMIENTO Y BACKEND)
    # ==========================================

    def actualizar_web():
        btn_actualizar.config(state="disabled", text="⌛ Sincronizando...", bg="#94a3b8")
        btn_abrir_web.config(state='disabled')
        barra_progreso.start(10)  
        root.update() 
        
        try:
            resultado = ejecucion_final()
            
            if resultado == True: 
                messagebox.showinfo(title="✅ Éxito", message='Web actualizada correctamente')
                estado.config(text="✅ Web actualizada correctamente", fg="#059669")
                barra_progreso.stop()
                barra_progreso['value'] = 100
                cargar_datos_pendientes() # Recargar la tabla tras actualizar la web
            else:
                messagebox.showerror(title="❌ Error", message='No se pudo actualizar. Revisa tu conexión a internet.')
                estado.config(text='❌ Error de conexión', fg='red')
                barra_progreso.stop()
                barra_progreso['value'] = 0
                
        except Exception as e:
            messagebox.showerror(title="❌ Error", message=f'Error: {str(e)[:100]}')
            estado.config(text='❌ Error en el proceso', fg='red')
            barra_progreso.stop()
            barra_progreso['value'] = 0
        finally:
            btn_actualizar.config(state="normal", text="🔄 Actualizar Web", bg="#2563eb")
            btn_abrir_web.config(state='normal')
    
    def abrir_web():
        try:
            ruta = 'https://leonardotovar853-lgtm.github.io/biblioteca-olga-bayone.io'
            webbrowser.open(ruta)
            messagebox.showinfo(title="🌐 Navegador", message='Web abierta correctamente')
            estado.config(text="🌐 Web abierta en el navegador", fg="#2563eb")
        except Exception as e:
            messagebox.showerror(title="❌ Error", message='No se encontró el archivo index.html')
            estado.config(text='❌ No se encontró la web', fg='red')

    def obtener_fila_seleccionada():
        """Devuelve el ID visual del Treeview y su fila correspondiente en Google Sheets."""
        seleccion = tree_pendientes.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, selecciona un registro de la lista.")
            return None, None
        
        item_id = seleccion[0]
        valores = tree_pendientes.item(item_id, 'values')
        num_fila_sheets = int(valores[-1])  
        return item_id, num_fila_sheets

    def cambiar_estado_registro(nuevo_estado):
        """Actualiza el estado en Sheets (Columna H / 8) y lo borra de la tabla visual."""
        item_id, fila_idx = obtener_fila_seleccionada()
        if not fila_idx:
            return
        
        if nuevo_estado == "Rechazado" and not messagebox.askyesno("Confirmar", "¿Estás seguro de rechazar este recurso?"):
            return

        try:
            if sheet:
                COLUMNA_ESTADO = 8 # Columna H de tu BD_general
                sheet.update_cell(fila_idx, COLUMNA_ESTADO, nuevo_estado)
                tree_pendientes.delete(item_id)
                messagebox.showinfo("Éxito", f"Recurso marcado como: {nuevo_estado}")
            else:
                messagebox.showwarning("Modo Offline", "No hay conexión con la base de datos.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar los datos: {e}")

    def exportar_reporte_csv():
        """Exporta el Treeview a un CSV local."""
        items = tree_pendientes.get_children()
        if not items:
            messagebox.showwarning("Reporte Vacío", "No hay datos en la bandeja para exportar.")
            return
        
        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")],
            initialfile=f"reporte_pendientes_{datetime.now().strftime('%Y%m%d')}.csv",
            title="Guardar Reporte Administrativo"
        )
        
        if ruta_archivo:
            try:
                with open(ruta_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
                    escritor = csv.writer(archivo_csv)
                    escritor.writerow(["Título", "Autor", "Categoría", "Enlace Recurso"])
                    
                    for item in items:
                        valores = tree_pendientes.item(item, 'values')
                        escritor.writerow(valores[:-1])  
                        
                messagebox.showinfo("Reporte Creado", f"Reporte guardado con éxito en:\n{ruta_archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el reporte: {e}")

    def cargar_datos_pendientes():
        """Lee el Sheets General con diagnóstico en consola."""
        for item in tree_pendientes.get_children():
            tree_pendientes.delete(item)
            
        if sheet:
            try:
                registros = sheet.get_all_records()
                
                if registros:
                    print("\n🔍 --- DIAGNÓSTICO DE COLUMNAS ---")
                    print("Columnas detectadas en tu Sheets:", list(registros[0].keys()))
                    print("-----------------------------------\n")
                else:
                    print("⚠️ La hoja 'BD_General' está completamente vacía.")
                    return

                contador_pendientes = 0
                for index, fila in enumerate(registros):
                    num_fila_real_sheets = index + 2 
                    
                    # Buscamos 'Estado' ignorando mayúsculas/minúsculas y espacios basura
                    estado_llave = next((k for k in fila.keys() if k.strip().lower() == 'estado'), None)
                    
                    if estado_llave:
                        estado_recurso = str(fila[estado_llave]).strip()
                    else:
                        print(f"❌ ERROR: No se encontró ninguna columna llamada 'Estado' en la fila {num_fila_real_sheets}")
                        continue
                    
                    # REVISIÓN DE TEXTO EXACTO:
                    # Comparamos quitando espacios y pasando a minúsculas para asegurar
                    if estado_recurso.lower() == 'pendiente':
                        contador_pendientes += 1
                        
                        # Extraemos los datos con valores seguros por si cambian las cabeceras
                        titulo_limpio = str(fila.get('Título', fila.get('Titulo', 'Sin Título'))).strip().title()
                        autor_limpio = str(fila.get('Autor', 'Sin Autor')).strip().title()
                        cat_limpia = str(fila.get('Área de Conocimiento', 'General')).strip().title()
                        link_recurso = str(fila.get('Enlace del recurso', '')).strip()
                        
                        valores_tabla = (titulo_limpio, autor_limpio, cat_limpia, link_recurso, num_fila_real_sheets)
                        tree_pendientes.insert("", "end", values=valores_tabla)
                
                print(f"📊 Registros procesados: {len(registros)} | Encontrados como 'Pendiente': {contador_pendientes}")
                
            except Exception as e:
                print(f"❌ Error cargando datos reales: {e}")
    # ==========================================
    # ARQUITECTURA VISUAL: CONTENEDOR DE PESTAÑAS (NOTEBOOK)
    # ==========================================
    
    style = ttk.Style()
    style.configure("TNotebook", background="#f1f5f9", padding=10)
    style.configure("TNotebook.Tab", font=("Helvetica", 11), padding=[15, 5])

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=15, pady=15)

    # --- PESTAÑA 1: CATÁLOGO GENERAL Y ACTUALIZACIÓN ---
    tab_catalogo = tk.Frame(notebook, bg="white")
    notebook.add(tab_catalogo, text="📚 Catálogo General")

    frame_interior = tk.Frame(tab_catalogo, bg="white", padx=30, pady=30)
    frame_interior.place(relx=0.5, rely=0.5, anchor="center")
    
    titulo = tk.Label(frame_interior, text='Biblioteca Digital Olga Bayone', font=("Helvetica", 20, "bold"), fg='black', bg='white')
    titulo.pack(pady=(0,10))
    
    desc = tk.Label(frame_interior, text="Sincroniza los datos de Google Sheets\ny actualiza el catálogo web automáticamente.", font=("Helvetica", 12), bg="white", fg="#4b5467", justify="center")
    desc.pack(pady=(0,20))
    
    estado = tk.Label(frame_interior, text='⚡ Listo para actualizar', font=("Helvetica", 11, "bold"), bg="white", fg="#2563eb")
    estado.pack(pady=(0,15))
    
    barra_progreso = ttk.Progressbar(frame_interior, mode='indeterminate', length=400)
    barra_progreso.pack(pady=(0,15))
    
    btn_actualizar = tk.Button(frame_interior, text='🔄 Actualizar Web', bg='#2563eb', command=actualizar_web, font=("Helvetica", 12, "bold"), fg='white', padx=20, pady=12, relief="flat", cursor="hand2", activebackground='#1d4ed8')
    btn_actualizar.pack(pady=(0,15))
    
    btn_abrir_web = tk.Button(frame_interior, text='🌐 Abrir Página Principal', bg='white', fg='#2563eb', font=("Helvetica", 11), command=abrir_web, padx=15, pady=8, relief="flat", cursor="hand2", activebackground='#e6f0ff', bd=1, highlightbackground='#cbd5e1')
    btn_abrir_web.pack(pady=(0,10))
    
    info_label = tk.Label(frame_interior, text="ℹ️ Los datos se obtienen de Google Sheets y se actualizan automáticamente", font=("Helvetica", 8), bg="white", fg="#94a3b8", wraplength=400)
    info_label.pack(pady=(15,0))

    # --- PESTAÑA 2: BANDEJA DE ENTRADA (PENDIENTES) ---
    tab_bandeja = tk.Frame(notebook, bg="white", padx=20, pady=20)
    notebook.add(tab_bandeja, text="📋 Bandeja de Entrada")

    lbl_instruccion = tk.Label(tab_bandeja, text="Recursos pendientes por revisión y aprobación institucional:", font=("Helvetica", 12, "bold"), bg="white", fg="#1e293b")
    lbl_instruccion.pack(anchor="w", pady=(0,10))

    columnas = ("titulo", "autor", "categoria", "enlace", "fila_sheets")
    tree_pendientes = ttk.Treeview(tab_bandeja, columns=columnas, show="headings", height=12)
    
    tree_pendientes.heading("titulo", text="Título del Libro")
    tree_pendientes.heading("autor", text="Autor")
    tree_pendientes.heading("categoria", text="Categoría")
    tree_pendientes.heading("enlace", text="Enlace del Recurso")
    tree_pendientes.heading("fila_sheets", text="ID Interno")

    tree_pendientes.column("titulo", width=200, anchor="w")
    tree_pendientes.column("autor", width=130, anchor="w")
    tree_pendientes.column("categoria", width=100, anchor="center")
    tree_pendientes.column("enlace", width=180, anchor="w")
    tree_pendientes.column("fila_sheets", width=0, stretch=False)  

    tree_pendientes.pack(fill="both", expand=True, pady=(0,15))

    frame_botones = tk.Frame(tab_bandeja, bg="white")
    frame_botones.pack(fill="x", side="bottom")

    btn_aprobar = tk.Button(frame_botones, text="✅ Aprobar Recurso", bg="#10b981", fg="white", font=("Helvetica", 11, "bold"), padx=15, pady=8, relief="flat", cursor="hand2", command=lambda: cambiar_estado_registro("Aprobado"))
    btn_aprobar.pack(side="left", padx=(0,10))

    btn_rechazar = tk.Button(frame_botones, text="❌ Rechazar", bg="#ef4444", fg="white", font=("Helvetica", 11, "bold"), padx=15, pady=8, relief="flat", cursor="hand2", command=lambda: cambiar_estado_registro("Rechazado"))
    btn_rechazar.pack(side="left")

    btn_reporte = tk.Button(frame_botones, text="📥 Exportar CSV", bg="#f8fafc", fg="#475569", font=("Helvetica", 11), padx=15, pady=8, relief="flat", cursor="hand2", bd=1, highlightbackground='#cbd5e1', command=exportar_reporte_csv)
    btn_reporte.pack(side="right")

    # CARGA INICIAL DE DATOS REALES DE LA BD
    cargar_datos_pendientes()

    # CENTRAR LA VENTANA AL ABRIR
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == '__main__':
    abrir_panel()