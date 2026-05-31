// 1. Inicializamos Google una sola vez al cargar la página
google.accounts.id.initialize({
    client_id: "520347031267-ph0fosq8l2ngoinasnm4b914vnrbqk1k.apps.googleusercontent.com",
    ux_mode: 'popup',
    itp_support: true,
    callback: async (response) => {
        // Decodificación del JWT de Google
        const base64Url = response.credential.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));

        const payload = JSON.parse(jsonPayload);
        
        // Guardamos los datos nativos de Google agregando el ID único ('sub')
        window.datosGoogle = { 
            id: payload.sub, 
            given_name: payload.given_name,
            email: payload.email,
            picture: payload.picture,
            credential: response.credential 
        };

        const divGoogle = document.querySelector('.ventana-registro #div-google');
        const divLogin = document.querySelector('.ventana-registro #contenedor-login');
        const divSeccionRegistro = document.querySelector('.ventana-registro #seccion-registro');

        if (payload.email.endsWith('@olgabayone.com')) {
            try {
                // CORRECCIÓN 1: Apuntar al endpoint real de verificación del backend
                const loginRespuesta = await fetch('http://localhost:5000/api/verificar-usuario', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: payload.sub }) 
                });
                const loginData = await loginRespuesta.json();

                // Si el servidor responde que el usuario ya existe en Google Sheets
                if (loginRespuesta.ok && loginData.existe) {
                    alert(`Bienvenido de vuelta, ${loginData.usuario.nombre}`);
                    localStorage.setItem('bibliotecaUsuario', JSON.stringify(loginData.usuario));
                    
                    const overlayActual = document.querySelector('.modal-overlay');
                    if (overlayActual) document.body.removeChild(overlayActual);
                    window.location.reload();
                    return;
                }
            } catch (error) {
                console.warn('No se pudo verificar el usuario automáticamente:', error);
            }

            // Si no existe, desplegamos el formulario escolar de la Olga Bayone
            if(divGoogle && divSeccionRegistro) {
                divGoogle.style.display = 'none';
                divSeccionRegistro.style.display = 'block';
                divSeccionRegistro.querySelector('h2').innerText = `Hola, ${payload.given_name}`;
            } else {
                // Si el modal aún no está abierto, guardamos el nombre para cuando se muestre
                window.pendingDatosGoogle = { given_name: payload.given_name };
            }
        } else {
            alert("Acceso denegado: Usa tu cuenta institucional @olgabayone.com");
            if(divGoogle && divLogin) {
                divGoogle.style.display = 'none';
                divLogin.style.display = 'block';
            }
        }
    }
});

function Registro() {
    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";
    
    const VentanaRegistro = document.createElement("div");
    VentanaRegistro.className = "ventana-registro";
    
    VentanaRegistro.innerHTML = `
    <button class="btn-cerrar">×</button>
    <div id="contenedor-login">
        <h2>Bienvenido</h2>
        <p>Usa tu cuenta institucional para explorar la biblioteca.</p>
        <button id="google-login-btn" class="btn-google-auth">
            <img src="../google-icon.png" alt="G" width="20" style="vertical-align: middle; margin-right: 8px;">
            Continuar con Google
        </button>
    </div>
    <div id="div-google" style="display: none;">
        <h2>Autenticando...</h2>
        <p>Verificando cuenta @olgabayone.com</p>
    </div>
    <div id="seccion-registro" style="display: none;">
        <h2>Completa tu Perfil</h2>
        <input type="number" id="reg-cedula" placeholder="Cédula de Identidad" class="input-registro">
        <select id="reg-rol" class="input-registro">
            <option value="" disabled selected>Selecciona tu rol</option>
            <option value="estudiante">Estudiante</option>
            <option value="profesor">Profesor</option>
        </select>
        <select id="reg-anio" class="input-registro">
            <option value="" disabled selected>Año y Sección</option>
            <option value="5A">5to Año A</option>
            <option value="5B">5to Año B</option>
            <option value="5C">5to Año C</option>
            <option value="no_aplica">No Aplica (Docentes)</option>
        </select>
        <button id="btn-enviar-registro" class="btn-iniciar-sesion">Finalizar Registro</button>
    </div>`;

    overlay.appendChild(VentanaRegistro);
    document.body.appendChild(overlay);

    // Si ya nos autenticaron antes de abrir el modal, sincronizamos la vista
    if (window.datosGoogle || window.pendingDatosGoogle) {
        const divGoogle = VentanaRegistro.querySelector('#div-google');
        const divSeccionRegistro = VentanaRegistro.querySelector('#seccion-registro');
        const contenedorLogin = VentanaRegistro.querySelector('#contenedor-login');

        if (divGoogle) divGoogle.style.display = 'none';
        if (divSeccionRegistro) {
            divSeccionRegistro.style.display = 'block';
            const nombre = window.datosGoogle?.given_name || window.pendingDatosGoogle?.given_name || '';
            const h2 = divSeccionRegistro.querySelector('h2');
            if (h2 && nombre) h2.innerText = `Hola, ${nombre}`;
        }
        if (contenedorLogin) contenedorLogin.style.display = 'none';
    }

    // Al hacer clic en Continuar con Google
    VentanaRegistro.querySelector('#google-login-btn').onclick = () => {
        VentanaRegistro.querySelector('#contenedor-login').style.display = 'none';
        const divGoogle = VentanaRegistro.querySelector('#div-google');
        divGoogle.style.display = 'block';

        try {
            if (!window.google?.accounts?.id) {
                throw new Error('Google Identity Services no cargado');
            }
            google.accounts.id.prompt(); 
        } catch (error) {
            console.error('Error al inicializar Google Sign-In:', error);
            alert('No se pudo iniciar Google Sign-In. Asegúrate de estar usando http://localhost.');
            divGoogle.style.display = 'none';
            VentanaRegistro.querySelector('#contenedor-login').style.display = 'block';
        }
    };

    // Botón Finalizar Registro (CONEXIÓN ADAPTADA A TU CLASE SERVIDOR EN PYTHON)
    VentanaRegistro.querySelector('#btn-enviar-registro').onclick = async () => {
        // Asegurarnos de que el usuario se haya autenticado con Google
        if (!window.datosGoogle || !window.datosGoogle.id) {
            alert('Debes iniciar sesión con Google antes de finalizar el registro.');
            return;
        }
        const cedula = VentanaRegistro.querySelector('#reg-cedula').value;
        const rol = VentanaRegistro.querySelector('#reg-rol').value;
        const anio = VentanaRegistro.querySelector('#reg-anio').value;

        if (!cedula || !rol || !anio) {
            alert("Por favor, rellena todos los campos antes de finalizar.");
            return;
        }

        // CORRECCIÓN 2: Mapear los nombres de variables exactos que espera tu backend
        const datosUsuario = {
            id: window.datosGoogle?.id, // Envía el string 'sub'
            nombre: window.datosGoogle?.given_name,
            correo: window.datosGoogle?.email,
            foto_url: window.datosGoogle?.picture,
            cedula: cedula,
            rol: rol,
            anio_seccion: anio
        };

        try {
            // CORRECCIÓN 3: Apuntar al puerto y endpoint correcto de registro de tu app Python
            const respuesta = await fetch('http://localhost:5000/agregar_usuario', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(datosUsuario)
            });

            const resultado = await respuesta.json();

            if (respuesta.ok) {
                alert(`¡Registro exitoso! Bienvenido, ${datosUsuario.nombre}.`);
                // Guardamos el objeto plano en localStorage para persistencia del cliente
                localStorage.setItem('bibliotecaUsuario', JSON.stringify(datosUsuario));
                document.body.removeChild(overlay);
                window.location.reload();
            } else {
                // Muestra el mensaje de error arrojado por tus validaciones @property de Python
                alert(`Error en el sistema: ${resultado.error || resultado.mensaje}`);
            }
        } catch (error) {
            console.error("Error al conectar con el backend:", error);
            alert("Hubo un problema de red al procesar tu cuenta.");
        }
    };

    // Eventos de cierre del Modal
    VentanaRegistro.querySelector('.btn-cerrar').onclick = () => document.body.removeChild(overlay);
    overlay.onclick = (e) => {
        if (e.target === overlay) document.body.removeChild(overlay);
    };
}

// Activar el botón de la barra de navegación web
const botonLogin = document.querySelector('.btn-registro');
if (botonLogin) {
    botonLogin.onclick = (e) => {
        e.preventDefault();
        Registro();
    };
}