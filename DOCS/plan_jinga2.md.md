# 📚 Plan de Migración a Plantillas Jinja2 - Biblioteca Digital Olga Bayone

Este documento detalla la estrategia, el cronograma y el mapa de arquitectura para refactorizar la generación del frontend estático de la biblioteca digital utilizando el motor de plantillas **Jinja2**.

---

## 📋 Diagnóstico de la Arquitectura Actual
Actualmente, el proyecto genera su frontend estático de la siguiente manera:
1. **HTML embebido en Python:** `BACKEND/creador_web.py` contiene más de 450 líneas de cadenas de texto HTML hardcodeadas (`html_inicio_catalogo`, `html_fin_catalogo`, etc.).
2. **HTML disperso en clases:** En `BACKEND/modelos.py`, cada subclase de `RecursoAcademico` (*Libro*, *Tesis*, *GuiaEstudio*, etc.) implementa su propio método `generar_tarjeta_html()` con f-strings.
3. **Duplicación de código:** El menú de navegación (`<nav id="menu">`), el pie de página (`<footer>`), las hojas de estilos CSS y los archivos de script JS comunes están duplicados en cada uno de los archivos del frontend. Si se desea cambiar el menú, se debe modificar en múltiples archivos y cadenas de texto de Python.

---

## 🚀 Ventajas de la Solución con Jinja2
1. **Separación de responsabilidades:** El código HTML vive en archivos `.html` dedicados con resaltado de sintaxis, autocompletado y validación, mientras que el código Python solo maneja la lógica.
2. **Herencia de Plantillas (`{% extends %}`):** Crearemos una plantilla maestra (`base.html`) que contiene la estructura HTML base, el menú y el footer. Las demás páginas heredarán de esta, eliminando la duplicación.
3. **Tarjeta Dinámica de Recursos (Macros/Includes):** Centralizaremos el diseño de la tarjeta en una sola plantilla de Jinja2, usando condicionales (`{% if recurso.tipo == 'Tesis' %}`) para renderizar los detalles específicos de cada recurso.
4. **Simplificación extrema del backend:** El generador `creador_web.py` pasará de ser un script complejo de concatenación de texto a una rutina elegante de menos de 100 líneas de código.

---

## 📂 Estructura de Archivos del Proyecto

La migración conservará la lógica del backend y los recursos del frontend (CSS/JS/Imágenes), pero centralizará la maquetación HTML en la carpeta del backend.

```text
PROYECTO_BIBLIOTECA_DIGITAL/
│
├── index.html                   # Redirección estática a FRONTEND/html/index.html
├── requirements.txt             # Dependencias (Flask ya incluye Jinja2)
│
├── DATA/                        # Archivos de datos y credenciales de APIs
│   ├── credenciales.json
│   └── biblioteca-olga-bayone-firebase-key.json
│
├── FRONTEND/                    # Destino de los HTML compilados y recursos estáticos
│   ├── css/                     # Hojas de estilo (No se modifican)
│   ├── js/                      # Archivos de lógica Javascript (No se modifican)
│   ├── html/                    # ¡IMPORTANTE! Aquí se escribirán los HTML compilados por Jinja2
│   │   ├── index.html           # <-- Generado automáticamente por Jinja2
│   │   ├── catalogo.html        # <-- Generado automáticamente por Jinja2
│   │   ├── repositorio.html     # <-- Generado automáticamente por Jinja2
│   │   ├── multimedia.html      # <-- Generado automáticamente por Jinja2
│   │   ├── sobre_proyecto.html  # <-- Generado automáticamente por Jinja2
│   │   └── agregar_libro.html   # <-- Generado automáticamente por Jinja2
│   └── imágenes/
│
└── BACKEND/                     # Procesamiento lógico y plantillas fuentes
    ├── creador_web.py           # Reescrito para usar Jinja2 Engine
    ├── modelos.py               # Simplificado (Se eliminan f-strings de HTML)
    ├── Panel_control.py         # Interfaz administrativa en Tkinter (Llama a creador_web.py)
    │
    └── templates/               # 🆕 CARPETA DE PLANTILLAS JINJA2
        ├── base.html            # Layout maestro (Contiene Navbar, Footer, Scripts comunes)
        ├── index.html           # Plantilla del Inicio (Hereda de base.html)
        ├── catalogo.html        # Plantilla de Catálogo (Hereda de base.html)
        ├── repositorio.html     # Plantilla de Repositorio (Hereda de base.html)
        ├── multimedia.html      # Plantilla de Multimedia (Hereda de base.html)
        ├── sobre_proyecto.html  # Plantilla de Sobre el Proyecto (Hereda de base.html)
        ├── agregar_libro.html   # Plantilla de Agregar Recurso (Hereda de base.html)
        │
        └── components/          # 🆕 Componentes reutilizables
            └── tarjeta.html     # Plantilla unificada de tarjeta con condicionales



                ┌────────────────────────┐
               │ Google Sheets          │
               │ (Base de Datos Nube)   │
               └───────────┬────────────┘
                           │ (Descarga de datos limpios)
                           ▼
               ┌────────────────────────┐
               │ admin_datos.py         │
               │ (Limpieza y Objetos)   │
               └───────────┬────────────┘
                           │
                           ▼ (Instancias de RecursoAcademico)
               ┌────────────────────────┐
               │ creador_web.py         │
               │ (Controlador Jinja2)   │
               └─────┬────────────┬─────┘
                     │            │
 (Carga Plantillas)  │            │ (Envía variables de datos:
                     ▼            │  recursos, libros_data, etc.)
┌───────────────────────────┐     │
│ BACKEND/templates/        │     ▼
│   ├── base.html           │ ┌────────────────────────┐
│   ├── catalogo.html       │─▶│      Jinja2 Engine     │
│   ├── components/         │ │ (Motor de Renderizado) │
│   │   └── tarjeta.html    │ └───────────┬────────────┘
└───────────────────────────┘             │
                                          │ (Renderiza e inyecta)
                                          ▼
                                ┌────────────────────────┐
                                │ FRONTEND/html/         │
                                │ (Archivos Compilados   │
                                │  100% Autónomos)       │
                                └────────────────────────┐