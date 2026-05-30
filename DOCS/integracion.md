# Guía de Integración - Sistema de Autenticación

## Biblioteca Digital - Colegio Olga Bayón de Evans

Esta guía te explica paso a paso cómo integrar el sistema de cuentas de estudiantes y profesores en tu biblioteca digital existente.

---

## 📁 Archivos Entregados

| Archivo | Descripción |
|---------|-------------|
| `login.html` | Página de login y registro (diseño moderno, responsive) |
| `auth.js` | Manejo de sesiones, protección de páginas, barra de usuario |
| `user_manager.py` | Script Python para gestionar usuarios en Google Sheets |
| `backend.gs` | Google Apps Script (Web App) que actúa como backend API |
| `integracion.md` | Esta guía |

---

## 🏗️ Arquitectura Recomendada

Como tu proyecto ya usa **Google Sheets** como base de datos y **Python** para generar HTML estático, la opción más sencilla y elegante es usar un **Google Apps Script Web App** como backend. Esto significa:

- No necesitas instalar servidores
- Todo queda dentro del ecosistema de Google
- Funciona con tu flujo actual de trabajo

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  login.html  │────▶│  backend.gs  │────▶│ Google Sheet │
│   auth.js    │◄────│  (Web App)   │◄────│  (Usuarios)  │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## 🔧 Paso 1: Preparar la Hoja de Usuarios

### Opción A - Con Python (recomendado si ya tienes el entorno)

1. Asegúrate de tener instalado:
   ```bash
   pip install gspread google-auth
   ```

2. En `user_manager.py`, reemplaza el `SPREADSHEET_ID` con el ID de tu hoja de Google Sheets actual (la misma que usas para los libros):
   ```python
   SPREADSHEET_ID = "1A2B3C4D..."  # Tu ID real
   ```

3. Coloca tu archivo `credentials.json` (cuenta de servicio de Google Cloud) en la misma carpeta.

4. Ejecuta:
   ```bash
   python user_manager.py --setup
   ```
   Esto creará automáticamente una pestaña llamada **"Usuarios"** en tu hoja.

### Opción B - Manual

1. Abre tu hoja de Google Sheets existente.
2. Crea una nueva pestaña llamada `Usuarios`.
3. En la fila 1, escribe estos encabezados:
   ```
   A1: ID | B1: Nombre | C1: Email | D1: Rol | E1: PasswordHash | F1: FechaRegistro | G1: Activo
   ```

---

## 🔧 Paso 2: Desplegar el Backend (Google Apps Script)

Este es el paso más importante. El `backend.gs` recibirá las peticiones de login/registro desde la página web.

1. Ve a [script.google.com](https://script.google.com)
2. Crea un **proyecto nuevo** (botón +)
3. Borra el código por defecto y **pega todo el contenido de `backend.gs`**
4. **Reemplaza** la línea:
   ```javascript
   const CONFIG = {
     SHEET_ID: 'TU_SPREADSHEET_ID_AQUI',
   ```
   con tu ID real de Google Sheets.
5. Guarda el proyecto (Ctrl+S o el ícono 💾)
6. Haz clic en **"Implementar"** (Deploy) → **"Nueva implementación"** (New deployment)
7. En el icono de engranaje ⚙️, selecciona **"Aplicación web"** (Web app)
8. Configura:
   - **Descripción**: `Auth Biblioteca Digital`
   - **Ejecutar como**: Yo (tú)
   - **Acceso**: Cualquiera (o "Cualquiera dentro de dominio" si tu colegio tiene Google Workspace)
9. Copia la **URL de la aplicación web** (algo como `https://script.google.com/macros/s/AKfycb.../exec`)

---

## 🔧 Paso 3: Configurar auth.js

Abre `auth.js` y busca esta línea:

```javascript
API_URL: localStorage.getItem('auth_api_url') || 'https://script.google.com/macros/s/TU_SCRIPT_ID/exec',
```

Reemplázala con la URL que copiaste en el paso anterior:

```javascript
API_URL: 'https://script.google.com/macros/s/AKfycbxxxxxxxxxxxxxxxx/exec',
```

---

## 🔧 Paso 4: Integrar en tu Proyecto Existente

Copia estos archivos a la carpeta donde generas tu HTML:

```
tu-proyecto/
├── index.html          ← tu biblioteca actual
├── login.html          ← NUEVO (copiar)
├── auth.js             ← NUEVO (copiar)
├── libros/             ← tus archivos actuales
└── ...
```

### 4.1 Proteger tu Biblioteca (index.html)

En el `<head>` de tu `index.html` (o cualquier página que quieras proteger), agrega:

```html
<script src="auth.js"></script>
<script>
  // Si el usuario no está logueado, redirige al login
  if (!Auth.isAuthenticated()) {
    window.location.href = 'login.html';
  }
</script>
```

### 4.2 Agregar barra de usuario

Tu `index.html` debe incluir `auth.js` para que aparezca la barra de usuario en la parte superior:

```html
<head>
  <script src="auth.js"></script>
</head>
```

La barra aparece automáticamente en todas las páginas que incluyan `auth.js` (excepto `login.html`).

### 4.3 Enlaces a la biblioteca

Desde `login.html`, el enlace **"Volver a la Biblioteca"** ya apunta a `index.html`. Asegúrate de que esa sea la ruta correcta de tu página principal.

---

## 🔧 Paso 5: Probar el Sistema

1. Abre `login.html` en tu navegador
2. Ve a la pestaña **"Registrarse"**
3. Crea una cuenta de prueba:
   - Nombre: `Usuario Prueba`
   - Email: `prueba@olgabayone`
   - Rol: Estudiante (o Profesor)
   - Contraseña: `123456`
4. Ve a **"Iniciar Sesión"** e ingresa las credenciales
5. Deberías ser redirigido a `index.html` con la barra de usuario visible

---

## 🔧 Paso 6: Administrar Usuarios con Python

### Registrar usuarios en masa (desde consola)

```bash
# Registrar un estudiante
python user_manager.py --add "María García" "mariagarcia@olgabayone" "estudiante" "clave123"

# Registrar un profesor
python user_manager.py --add "Prof. López" "proflópez@olgabayone" "profesor" "clave123"

# Listar todos los usuarios
python user_manager.py --list

# Desactivar un usuario
python user_manager.py --deactivate "usuario@olgabayone"

# Restablecer contraseña
python user_manager.py --reset-password "usuario@olgabayone" "nuevaclave"
```

### Exportar usuarios para modo offline

Si alguna vez necesitas que el frontend valide sin conexión al backend:

```bash
python user_manager.py --export-json
```

Esto genera `users_data.json` con los datos públicos de los usuarios.

---

## 🎨 Personalización

### Cambiar colores

En `login.html`, modifica las variables CSS al inicio del `<style>`:

```css
:root {
  --primary: #1a56db;        /* Azul principal */
  --primary-dark: #1e429f;   /* Azul oscuro (hover) */
}
```

### Cambiar el nombre del colegio

Busca en `login.html`:

```html
<p>Colegio Olga Bayón de Evans</p>
```

### Agregar más campos al registro

Si necesitas guardar más datos (grado, sección, etc.):

1. Agrega la columna en la hoja de Google Sheets
2. Agrega el campo en `login.html`
3. Modifica `backend.gs` para recibir y guardar ese campo

---

## 🔒 Seguridad - Notas Importantes

1. **Contraseñas**: Nunca se guardan en texto plano. Se usa `SHA-256` para el hash. Para un sistema real, considera agregar "sal" (salt) al hash.

2. **Dominio restringido**: Solo se permiten correos que terminen en `@olgabayone`.

3. **HTTPS**: Asegúrate de que tu biblioteca esté servida por HTTPS (GitHub Pages, Netlify, etc.) para que las contraseñas viajen seguras.

4. **Sesiones**: Las sesiones duran 24 horas. Después de eso, el usuario debe volver a loguearse.

5. **Google Apps Script**: El backend ejecuta con tus permisos de Google. No compartas la URL del Web App públicamente si contiene datos sensibles.

---

## 🆘 Solución de Problemas

### "Error de conexión con el servidor"

- Verifica que la URL de `backend.gs` esté correcta en `auth.js`
- Abre la URL del backend directamente en el navegador; debería mostrar un mensaje JSON

### "No se puede acceder a la hoja"

- Comparte tu hoja de Google Sheets con el email del "service account" que aparece en `credentials.json`
- El email suele verse como `nombre@proyecto-123456.iam.gserviceaccount.com`

### Los usuarios no aparecen

- Verifica que la pestaña se llame exactamente `Usuarios` (con U mayúscula)
- Verifica que los encabezados coincidan exactamente con los que espera el código

---

## 🚀 Mejoras Futuras (Ideas para tu Tesis)

1. **Recuperación de contraseña**: Enviar email con token de restablecimiento usando `MailApp.sendEmail()` de Google Apps Script.

2. **Perfil de usuario**: Página donde el usuario puede ver su historial de libros consultados.

3. **Roles avanzados**: Los profesores podrían agregar libros, los estudiantes solo consultar.

4. **Google OAuth directo**: Si tu colegio usa Google Workspace, puedes usar OAuth 2.0 para login sin contraseñas.

5. **Logs de actividad**: Una pestaña adicional en Sheets que registre quién consultó qué libro y cuándo.

---

## ✅ Checklist Final

- [ ] `SPREADSHEET_ID` actualizado en `user_manager.py`
- [ ] `SHEET_ID` actualizado en `backend.gs`
- [ ] `API_URL` actualizado en `auth.js`
- [ ] Archivos `login.html` y `auth.js` copiados al proyecto
- [ ] `auth.js` incluido en `index.html`
- [ ] Prueba de registro exitosa
- [ ] Prueba de login exitosa
- [ ] Redirección a `index.html` funciona
- [ ] La barra de usuario aparece arriba
