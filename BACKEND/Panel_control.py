from creador_web import ejecucion_final
import tkinter as tk 
from tkinter import messagebox, ttk
import webbrowser
import os

def abrir_panel():  #Función Para Abrir el Panel de Control
    root = tk.Tk()
    
    # DEFINICIÓN: Función para Actualizar la web
    def actualizar_web():
        btn_actualizar.config(state="disabled", text="⌛ Sincronizando...", bg="#94a3b8")
        btn_abrir_web.config(state='disabled')
        barra_progreso.start(10)  
        root.update() 
        
        try:
            resultado = ejecucion_final()
            
            if resultado == True: 
                messagebox.showinfo(
                    title="✅ Éxito", 
                    message='Web actualizada correctamente'
                )
                estado.config(text="✅ Web actualizada correctamente", fg="#059669")
                barra_progreso.stop()
                barra_progreso['value'] = 100
            else:
                messagebox.showerror(  # ✅ CORREGIDO: showerror para errores
                    title="❌ Error", 
                    message='No se pudo actualizar. Revisa tu conexión a internet.'
                )
                estado.config(text='❌ Error de conexión', fg='red')
                barra_progreso.stop()
                barra_progreso['value'] = 0
                
        except Exception as e:
            messagebox.showerror(  # ✅ CORREGIDO: showerror para errores
                title="❌ Error", 
                message=f'Error: {str(e)[:100]}'
            )
            estado.config(text='❌ Error en el proceso', fg='red')
            barra_progreso.stop()
            barra_progreso['value'] = 0

        finally:
            btn_actualizar.config(state="normal", text="🔄 Actualizar Web", bg="#2563eb")
            btn_abrir_web.config(state='normal')
    
    def abrir_web():
        ruta = r'C:\Users\NEW DELL\Documents\PROGRAMACIÓN\PROYECTO_BIBLIOTECA_DIGITAL\FRONTEND\index.html'
        
        if os.path.exists(ruta):
            webbrowser.open(f'file://{ruta}')
            messagebox.showinfo(
                title="🌐 Navegador", 
                message='Web abierta correctamente'
            )
            estado.config(text="🌐 Web abierta en el navegador", fg="#2563eb")
        else:
            messagebox.showerror(
                title="❌ Error", 
                message='No se encontró el archivo index.html'
            )
            estado.config(text='❌ No se encontró la web', fg='red')
    
    # DISEÑO DEL PANEL
    frame = tk.Frame(
        root,
        bg="white",
        padx=40,
        pady=40, 
        highlightbackground="#e5e7eb",
        highlightthickness=1
    )
    frame.place(relx=0.5, rely=0.5, anchor="center")
    
    # TITULO
    titulo = tk.Label(
        frame,
        text='Biblioteca Digital Olga Bayone',
        font=("Helvetica", 20, "bold"),
        fg='black',
        bg='white'
    )
    titulo.pack(pady=(0,10))
    
    # DESCRIPCIÓN
    desc = tk.Label(
        frame, 
        text="Sincroniza los datos de Google Sheets\n y actualiza el catálogo web automáticamente.", 
        font=("Helvetica", 12), 
        bg="white", 
        fg="#4b5467",
        justify="center"
    )
    desc.pack(pady=(0,20))
    
    # ESTADO
    estado = tk.Label(
        frame,
        text='⚡ Listo para actualizar',
        font=("Helvetica", 11, "bold"),
        bg="white",
        fg="#2563eb"
    )
    estado.pack(pady=(0,15))
    
    # BARRA DE PROGRESO
    barra_progreso = ttk.Progressbar(
        frame,
        mode='indeterminate',
        length=400
    )
    barra_progreso.pack(pady=(0,15))
    
    # BOTÓN PRINCIPAL - ACTUALIZAR
    btn_actualizar = tk.Button(
        frame,
        text='🔄 Actualizar Web',  # ✅ CORREGIDO: 'Actualizar' con 'a'
        bg='#2563eb',
        command=actualizar_web,
        font=("Helvetica", 12, "bold"),
        fg='white',
        padx=20,
        pady=12,
        relief="flat",
        cursor="hand2",
        activebackground='#1d4ed8'
    )
    btn_actualizar.pack(pady=(0,15))
    
    # BOTÓN SECUNDARIO - ABRIR WEB
    btn_abrir_web = tk.Button(
        frame,
        text='🌐 Abrir Página Principal',
        bg='white',
        fg='#2563eb',
        font=("Helvetica", 11),
        command=abrir_web,
        padx=15,
        pady=8,
        relief="flat",
        cursor="hand2",
        activebackground='#e6f0ff',
        bd=1,
        highlightbackground='#cbd5e1'
    )
    btn_abrir_web.pack(pady=(0,10))
    
    # INFORMACIÓN ADICIONAL
    info_label = tk.Label(
        frame,
        text="ℹ️ Los datos se obtienen de Google Sheets y se actualizan automáticamente",
        font=("Helvetica", 8),
        bg="white",
        fg="#94a3b8",
        wraplength=400
    )
    info_label.pack(pady=(15,0))
    
    # CONFIGURACIÓN DEL PANEL DE CONTROL
    root.geometry("600x550")
    root.config(background='#f1f5f9')
    root.title('Panel de Control - Biblioteca Digital Olga Bayone')
    root.resizable(True, True)
    
    try:
        root.iconbitmap(r'C:\Users\NEW DELL\Documents\PROGRAMACIÓN\PROYECTO_BIBLIOTECA_DIGITAL\FRONTEND\logo_olga_bayone.ico')
    except:
        pass
    
    root.maxsize(800, 700)
    root.minsize(500, 500)
    
    # CENTRAR LA VENTANA
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == '__main__':
    abrir_panel()