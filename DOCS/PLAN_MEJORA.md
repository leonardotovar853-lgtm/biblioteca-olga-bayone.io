# PLAN DE MEJORA - BIBLIOTECA DIGITAL OLGA BAYONE

> **Versión:** 1.0  
> **Última actualización:** Julio 2026  
> **Estado:** Pendiente de implementación

---

## 📋 RESUMEN EJECUTIVO

Plan de mejoras para optimizar el backend (Flask + Jinja2) y el frontend (CSS/JS vanilla) de la Biblioteca Digital. Basado en análisis de código completo realizado el 01/07/2026.

---

## 🔧 MEJORAS DE BACKEND

### 1. Arquitectura y Código

| # | Mejora | Descripción | Prioridad | Tiempo est. |
|---|--------|-------------|-----------|-------------|
| 1.1 | **Módulo de caché de datos** | Reemplazar la variable global `biblioteca_global` en `app.py` por Flask-Caching con TTL. Hoy se recarga desde Google Sheets en cada arranque. | 🟡 Alta | 4-5h |
| 1.2 | **Completar `recomendaciones.py`** | El archivo ejecuta `convertir_data()` pero no usa el resultado. Implementar lógica de recomendaciones por área/autor. | 🟡 Alta | 2-3h |
| 1.3 | **Eliminar `html_templates.py`** | Archivo vacío (0 líneas). Era planeado antes de la migración a Jinja2. | 🟢 Baja | 5min |
| 1.4 | **Centralizar configuración en `config.py`** | Mover rutas hardcodeadas de `app.py` y `cuentas.py` a `config.py`. | 🟡 Media | 1-2h |
| 1.5 | **Sistema de logging** | Reemplazar `print()` por `logging` de Python con niveles (INFO, WARNING, ERROR). | 🟡 Media | 2-3h |

### 2. API y Rendimiento

| # | Mejora | Descripción | Prioridad | Tiempo est. |
|---|--------|-------------|-----------|-------------|
| 2.1 | **API de búsqueda** | Endpoint `/api/buscar?q=...` para bibliotecas grandes (+500 recursos). Hoy la búsqueda es 100% JS del lado cliente. | 🟡 Media | 4-5h |
| 2.2 | **Paginación en rutas** | Implementar `?page=1&limit=20` en catálogo, repositorio y multimedia. | 🟡 Alta | 3-4h |
| 2.3 | **Endpoint de estadísticas** | `/api/stats` devuelve totales: libros, tesis, multimedia, aprobados/pendientes. | 🟢 Baja | 1h |
| 2.4 | **Health check** | `/api/health` devuelve `{"status": "ok", "biblioteca_cargada": true/false}`. | 🟢 Baja | 30min |

### 3. Despliegue y Seguridad

| # | Mejora | Descripción | Prioridad | Tiempo est. |
|---|--------|-------------|-----------|-------------|
| 3.1 | **Variables de entorno en `.env`** | Mover credenciales a variables de entorno. Crear `.env.example`. | 🟡 Alta | 1h |
| 3.2 | **Actualizar `Dockerfile` a Python 3.12** | Hoy usa `python:3.10-slim`, pero `runtime.txt` dice 3.12. Consistencia. | 🟡 Media | 30min |
| 3.3 | **Middleware de CORS específico** | Especificar orígenes permitidos en lugar de CORS genérico. | 🟡 Media | 30min |
| 3.4 | **Rate limiting en API** | Proteger rutas POST con límites de peticiones. | 🟢 Baja | 2h |

---

## 🎨 MEJORAS DE FRONTEND

### 4. Rendimiento y Carga

| # | Mejora | Descripción | Prioridad | Tiempo est. |
|---|--------|-------------|-----------|-------------|
| 4.1 | **Minificar CSS/JS** | Los 7 CSS y 9 JS se cargan sin minificar. Usar Flask-Assets. | 🟡 Alta | 2-3h |
| 4.2 | **Carga asíncrona de datos** | Reemplazar `librosData` inyectado en HTML por `fetch('/api/buscar')`. | 🟡 Alta | 4-5h |
| 4.3 | **Lazy loading de imágenes** | Verificar `loading="lazy"` en banners y `sobre_proyecto.html`. | 🟢 Baja | 30min |
| 4.4 | **Precarga de FontAwesome** | Agregar `rel="preload"` al CDN de FontAwesome. | 🟢 Baja | 15min |

### 5. UX/UI y Diseño

| # | Mejora | Descripción | Prioridad | Tiempo est. |
|---|--------|-------------|-----------|-------------|
| 5.1 | **Modo oscuro** | Toggle de tema claro/oscuro con CSS custom properties. | 🟡 Media | 4-5h |
| 5.2 | **Spinner de carga** | Mostrar spinner mientras cargan datos vía API. | 🟡 Media | 1-2h |
| 5.3 | **Toast de notificaciones** | Reemplazar `alert()` por sistema de toast/snackbar. | 🟢 Baja | 2-3h |
| 5.4 | **Barra de progreso en subida** | Feedback visual en formularios de Google. | 🟢 Baja | 1h |

### 6. JavaScript y Funcionalidad

| # | Mejora | Descripción | Prioridad | Tiempo est. |
|---|--------|-------------|-----------|-------------|
| 6.1 | **Refactorizar JS en módulos** | Los 9 JS usan funciones globales. Migrar a módulos ES6. | 🟡 Media | 5-6h |
| 6.2 | **Unificar buscadores JS** | 3 buscadores separados (`buscador.js`, `buscadorRepositorio.js`, `buscador_multimedia.js`). Unificar. | 🟡 Alta | 4-5h |
| 6.3 | **Sistema de favoritos persistente** | Likes guardados en `localStorage` entre sesiones. | 🟡 Media | 2-3h |
| 6.4 | **Filtros en URL** | Filtros reflejados en URL con `history.pushState`. | 🟢 Baja | 2-3h |

---

## 🎯 PRIORIDADES RECOMENDADAS (PRÓXIMA SEMANA)

| Prioridad | Mejora | Tiempo est. | Dificultad |
|-----------|--------|-------------|------------|
| 🥇 | **1.2 Completar `recomendaciones.py`** | 2-3h | 🟢 Fácil |
| 🥇 | **6.2 Unificar buscadores JS** | 4-5h | 🟡 Media |
| 🥇 | **2.2 Paginación en rutas** | 3-4h | 🟡 Media |
| 🥇 | **4.1 Minificar CSS/JS** | 2-3h | 🟢 Fácil |
| 🥇 | **1.4 Centralizar config en `config.py`** | 1-2h | 🟢 Fácil |

---

## 📊 ESTADO ACTUAL DEL PROYECTO (RESUMEN)

### Backend (Python/Flask)
- ✅ **App Flask centralizada**: `app.py` con Jinja2 y Blueprint de autenticación
- ✅ **Migración a Jinja2 completa**: 7 templates + 1 macro de tarjeta
- ✅ **Despliegue en Render funcional**: Dockerfile + Procfile + wsgi.py
- ✅ **Google Sheets como fuente de datos**: 29 recursos cargados
- ❌ **`recomendaciones.py` incompleto**: función sin retorno
- ❌ **Caché de datos ausente**: variable global frágil
- ❌ **Logging no implementado**: prints esparcidos por el código

### Frontend (CSS/JS vanilla)
- ✅ **Diseño responsivo**: menú hamburguesa, grid de tarjetas, media queries
- ✅ **FontAwesome + Google Fonts**: iconos y tipografía Inter
- ❌ **3 buscadores separados**: código duplicado entre `buscador.js`, `buscadorRepositorio.js`, `buscador_multimedia.js`
- ❌ **Sin minificación**: 7 CSS + 9 JS sin comprimir
- ❌ **Funciones globales en JS**: sin modularización

### Infraestructura
- ✅ **Render (producción)**: `https://biblioteca-olga-bayone.onrender.com`
- ✅ **GitHub (código fuente)**: `https://github.com/leonardotovar853-lgtm/biblioteca-olga-bayone.io`
- ✅ **Firebase Realtime Database**: autenticación y sistema de likes
- ❌ **Python 3.10 vs 3.12 inconsistencia**: Dockerfile usa 3.10, runtime.txt 3.12

---

## 📁 ARCHIVOS DEL PROYECTO

```
PROYECTO_BIBLIOTECA_DIGITAL/
│
├── BACKEND/
│   ├── app.py                 # App Flask principal (Jinja2, rutas, Blueprint)
│   ├── cuentas.py             # Blueprint de autenticación (Firebase)
│   ├── admin_datos.py         # Conexión a Google Sheets + limpieza de datos
│   ├── modelos.py             # Modelos de datos puros (sin HTML)
│   ├── Panel_control.py       # GUI Tkinter (conexión a Render vía API)
│   ├── config.py              # Configuraciones centralizadas
│   ├── recomendaciones.py     # [INCOMPLETO] Lógica de recomendaciones
│   ├── sistemas_likes.py      # Sistema de likes (Firebase)
│   ├── html_templates.py      # [VACÍO] Eliminar
│   │
│   └── templates/             # Plantillas Jinja2
│       ├── base.html          # Plantilla base (navbar, footer)
│       ├── index.html         # Página de inicio
│       ├── catalogo.html      # Catálogo de libros
│       ├── repositorio.html   # Repositorio de tesis
│       ├── multimedia.html    # Archivos multimedia
│       ├── sobre_proyecto.html
│       ├── agregar_libro.html
│       └── components/
│           └── tarjeta.html   # Macro de tarjeta reutilizable
│
├── FRONTEND/
│   ├── css/       (7 archivos)
│   ├── js/        (9 archivos)
│   └── images/    (13 imágenes)
│
├── DATA/          (credenciales JSON)
├── DOCS/          (documentación)
│
├── Dockerfile
├── Procfile
├── requirements.txt
├── runtime.txt
├── wsgi.py
└── .gitignore
```