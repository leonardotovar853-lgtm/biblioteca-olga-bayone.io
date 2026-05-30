PROYECTO_BIBLIOTECA_DIGITAL/
│
├── app.py                      <-- Tu servidor de Flask actual
├── DATA/
│   └── credenciales.json       <-- Tus llaves de Google Sheets
│
├── templates/                  <-- NUEVA CARPETA (Obligatorio este nombre)
│   └── index.html              <-- Tu archivo HTML principal va aquí dentro
│
└── static/                     <-- NUEVA CARPETA (Obligatorio este nombre)
    ├── css/                    <-- Mueves tu carpeta de estilos aquí
    ├── js/                     <-- Mueves tu carpeta de JavaScript aquí
    ├── images/                 <-- Mueves tus imágenes aquí
    └── fonts/                  <-- Mueves tus fuentes aquí

# Biblioteca Digital Inteligente - U.E. Olga Bayone de Rodríguez

Plataforma web educativa diseñada para centralizar el catálogo de libros y el repositorio de proyectos de investigación institucionales de la U.E. Olga Bayone de Rodríguez.

## 🚀 Características
- **Autenticación Institucional:** Acceso restringido exclusivamente a estudiantes y profesores con cuentas `@olgabayone.com` mediante Google OAuth2.
- **Buscador Avanzado:** Sistema de filtrado en tiempo real programado en JavaScript para ubicar textos por título, autor o materia.
- **Base de Datos Remota:** Conexión directa y segura con Google Sheets mediante la API de gspread en el backend.
- **Arquitectura Híbrida:** Interfaz estática optimizada de alta velocidad combinada con un microservicio dinámico en Python y Flask.

## 🛠️ Tecnologías Utilizadas
- **Frontend:** HTML5, CSS3, JavaScript Vanilla.
- **Backend:** Python 3, Flask, Flask-CORS, Requests.
- **Persistencia y APIs:** Google Sheets API, Google Sign-In API, Pandas.

## 🧑‍💻 Autor
Desarrollado como Proyecto de Grado por **Leonardo Tovar** (5to Año).