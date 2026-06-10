# 📚 Documentación Técnica: Sistema de Biblioteca Digital Inteligente
**Institución:** U.E. Olga Bayone de Rodríguez  
**Desarrollador:** Leonardo Tovar  
**Año:** 2026  
**Estatus del Proyecto:** En Desarrollo (Fases de Backend y Arquitectura Completadas)

---

## 1. Arquitectura General del Sistema
El sistema está diseñado bajo una arquitectura desacoplada de dos capas principales (Frontend y Backend) para garantizar velocidad, escalabilidad y orden en el código fuente.

[ FRONTEND ] (GitHub Pages)
 HTML5 / CSS3 / JavaScript
             │
     Peticiones HTTP (Fetch)
             ▼
   [ BACKEND ] (Flask en Render)
   Manejo de Lógica y Seguridad
             │
      API de Google Sheets
             ▼
 [ BASE DE DATOS ] (Google Sheets)
 Almacenamiento Seguro de Datos

* **Frontend (Cliente):** Interfaz gráfica responsiva alojada en **GitHub Pages**. Controla el diseño web, las tarjetas de recursos y la interacción directa con el estudiante.
* **Backend (Servidor):** Microservidor desarrollado en **Python (Flask)**, alojado en **Render (Plan Free)**. Se encarga de procesar la lógica de negocios, la comunicación con APIs externas y el control de accesos.
* **Base de Datos:** **Google Sheets**, integrado mediante la API de Google Cloud para el almacenamiento de registros en tiempo real.

---

## 2. Repositorio y Seguridad del Código

### Estatus Legal y Propiedad Intelectual
El repositorio se configuró inicialmente con una licencia abierta MIT. Para proteger la propiedad intelectual de la tesis ante posibles plagios académicos, **se removió la licencia MIT**. El proyecto opera bajo el estatus de **Copyright Automático (Todos los derechos reservados)** bajo el marco del Convenio de Berna. La prueba legal de autoría queda respaldada por la bitácora cronológica de *commits* en la cuenta personal de GitHub.

### Buenas Prácticas de Seguridad Aplicadas
1.  **Uso de `.gitignore`:** Archivo clave para omitir la subida de archivos confidenciales (como llaves privadas del Sheets `credentials.json` o entornos virtuales) al servidor público de GitHub.
2.  **Variables de Entorno (`OS Environment`):** Se removieron las credenciales explícitas del código fuente (específicamente la variable `GOOGLE_CLIENT_ID` en `cuentas.py`). Ahora el servidor lee la credencial de forma segura desde el sistema operativo mediante:
    ```python
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    ```
    El valor real está resguardado de forma privada en el panel de variables de entorno de **Render**.

---

## 3. Sistema de Cuentas y Autenticación con Google

El flujo de inicio de sesión fue validado con éxito, logrando conectar la interfaz con el backend para almacenar de forma correcta los datos de registro en las hojas de cálculo de Google.

### Optimización de Sesión Activa (Persistencia)
Para evitar peticiones redundantes al servidor cada vez que la página web se actualiza, se diseñó un flujo de persistencia local en el navegador usando la API **`localStorage`**:

1.  **Al iniciar sesión con éxito:** Se extraen el nombre, correo y la URL de la foto de perfil del objeto `payload` de Google, se empaquetan en un objeto JSON y se guardan localmente:
    ```javascript
    localStorage.setItem('sesionBiblioteca', JSON.stringify(datosUsuario));
    ```
2.  **Al cargar la página (`DOMContentLoaded`):** El cliente verifica el espacio de memoria. Si detecta la sesión activa, salta el paso de inicio de sesión, actualiza la barra de navegación y renderiza dinámicamente la **Foto de Perfil del Usuario de Google** en formato redondo en la interfaz.

### Configuración del Servidor y CORS
Para permitir que la página oficial desplegada en internet se comunique con el backend en la nube sin restricciones del navegador, se configuró el control de acceso de orígenes cruzados en Flask (`flask_cors`):
```python
CORS(app, resources={r"/*": {"origins": "*"}})