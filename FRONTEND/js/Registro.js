function initializeGoogleAuth() {
    if (window.location.protocol === 'file:') {
        console.warn('Google Sign-In no se inicializará en file://. Usa un servidor local HTTP.');
        return;
    }

    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = () => {
        google.accounts.id.initialize({
            client_id: "520347031267-ph0fosq8l2ngoinasnm4b914vnrbqk1k.apps.googleusercontent.com",
            ux_mode: 'popup',
            itp_support: true,
            callback: async (response) => {
                // Guardamos el token en memoria global para usarlo en el formulario final si es necesario
                window.googleCredential = response.credential;

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

                // PERMITIR GMAIL PARA PRUEBAS LOCALES (Remover @gmail.com cuando esté en producción)
                if (payload.email.endsWith('@olgabayone.com') || payload.email.endsWith('@gmail.com')) {
                    try {
                        // CORRECCIÓN 1: Enviamos la credencial completa (Token) para validación segura en Python
                        const loginRespuesta = await fetch('http://localhost:5000/api/verificar-usuario', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ credential: response.credential }) 
                        });
                        const loginData = await loginRespuesta.json();

                        // Si el servidor responde que el usuario ya existe en Google Sheets
                        if (loginRespuesta.ok && loginData.existe) {
                            mostrarAlerta(`Bienvenido de vuelta, ${loginData.usuario.nombre}`, 'success');
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
                    mostrarAlerta("Acceso denegado: Usa tu cuenta institucional @olgabayone.com", 'error');
                    if(divGoogle && divLogin) {
                        divGoogle.style.display = 'none';
                        divLogin.style.display = 'block';
                    }
                }
            }
        });
    };
    document.head.appendChild(script);
}

function mostrarAlerta(mensaje, tipo = 'info', duracion = 4500) {
    const contenedor = document.querySelector('.custom-alert-container') || document.createElement('div');
    if (!contenedor.classList.contains('custom-alert-container')) {
        contenedor.className = 'custom-alert-container';
        document.body.appendChild(contenedor);
    }

    const alerta = document.createElement('div');
    alerta.className = `custom-alert custom-alert--${tipo}`;
    alerta.innerHTML = `
        <span class="custom-alert__texto">${mensaje}</span>
        <button type="button" class="custom-alert__close" aria-label="Cerrar">×</button>
    `;

    alerta.querySelector('.custom-alert__close').onclick = () => {
        alerta.classList.remove('mostrar');
        setTimeout(() => alerta.remove(), 200);
    };

    contenedor.appendChild(alerta);
    requestAnimationFrame(() => alerta.classList.add('mostrar'));

    setTimeout(() => {
        if (alerta.parentElement) {
            alerta.classList.remove('mostrar');
            setTimeout(() => alerta.remove(), 200);
        }
    }, duracion);
}

window.alert = (mensaje) => mostrarAlerta(String(mensaje), 'info');

initializeGoogleAuth();

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
            <i class="fa-brands fa-google" style="vertical-align: middle; margin-right: 8px; font-size: 20px;"></i>
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
        if (window.location.protocol === 'file:') {
            mostrarAlerta('Debes abrir la página mediante HTTP local (por ejemplo http://localhost:8000), no con file://.', 'error');
            return;
        }

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
            mostrarAlerta('No se pudo iniciar Google Sign-In. Asegúrate de estar usando http://localhost y de que la librería de Google esté cargada.', 'error');
            divGoogle.style.display = 'none';
            VentanaRegistro.querySelector('#contenedor-login').style.display = 'block';
        }
    };

    // Botón Finalizar Registro
    VentanaRegistro.querySelector('#btn-enviar-registro').onclick = async () => {
        // CORRECCIÓN: Validamos con la credencial cruda en memoria global
        if (!window.googleCredential) {
            mostrarAlerta('Debes iniciar sesión con Google antes de finalizar el registro.', 'error');
            return;

        }

        const cedula = VentanaRegistro.querySelector('#reg-cedula').value.trim();
        const rol = VentanaRegistro.querySelector('#reg-rol').value;
        const anio = VentanaRegistro.querySelector('#reg-anio').value;

        if (!cedula || !rol || !anio) {
            mostrarAlerta("Por favor, rellena todos los campos antes de finalizar.", 'error');
            return;
        }

        // CORRECCIÓN 2: Estructura recomendada enviando la credencial cruda para seguridad
        // Nota: Si tu backend ya está diseñado para recibir datos sueltos sin validar el token,
        // puedes dejar el objeto anterior, pero lo ideal por seguridad web es pasar 'credential'.
        const datosUsuario = {
            credential: window.googleCredential,
            cedula: cedula,
            rol: rol,
            anio_seccion: anio
        };

        try {
            // CORRECCIÓN 3: Asegúrate de que este endpoint coincida con tu backend en Flask
            const respuesta = await fetch('http://127.0.0.1:5000', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datosUsuario)
            });

            const resultado = await respuesta.json();

            if (respuesta.ok) {
                mostrarAlerta(`¡Registro exitoso! Perfil creado correctamente.`, 'success');
                // Guardamos el usuario retornado por Python para persistencia en frontend
                localStorage.setItem('bibliotecaUsuario', JSON.stringify(resultado.usuario));
                document.body.removeChild(overlay);
                window.location.reload();
            } else {
                mostrarAlerta(`Error en el sistema: ${resultado.error || resultado.mensaje}`, 'error');
            }
        } catch (error) {
            console.error("Error al conectar con el backend:", error);
            mostrarAlerta("Hubo un problema de red al procesar tu cuenta.", 'error');
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