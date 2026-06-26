const FIREBASE_CONFIG = {
    apiKey: "AIzaSyAcxfbhDpx4L8FXLrIlPSvOPVZXtlGpkmQ",
    authDomain: "biblioteca-olga-bayone.firebaseapp.com",
    databaseURL: "https://biblioteca-olga-bayone-default-rtdb.firebaseio.com",
    projectId: "biblioteca-olga-bayone",
    storageBucket: "biblioteca-olga-bayone.firebasestorage.app",
    messagingSenderId: "648373694244",
    appId: "1:648373694244:web:2d2a855d79d1614c568db1"
};

let firebaseAuthInstance = null;

function initializeFirebaseAuth() {
    if (window.location.protocol === 'file:') {
        console.warn('Firebase Auth no se inicializará en file://. Usa un servidor local HTTP.');
        return;
    }

    if (!window.firebase || !window.firebase.auth) {
        console.error('Firebase SDK no está disponible. Revisa los scripts en tu HTML.');
        return;
    }

    if (!firebase.apps.length) {
        firebase.initializeApp(FIREBASE_CONFIG);
    }

    firebaseAuthInstance = firebase.auth();
    firebaseAuthInstance.onAuthStateChanged(user => {
        if (user) {
            const usuarioGuardado = JSON.parse(localStorage.getItem('bibliotecaUsuario'));
            if (!usuarioGuardado) {
                localStorage.setItem('bibliotecaUsuario', JSON.stringify({
                    id: user.uid,
                    nombre: user.displayName,
                    correo: user.email,
                    foto_url: user.photoURL,
                    rol: null,
                    anio_seccion: null,
                    intereses: [],
                    fecha_registro: null
                }));
            }
        }
    });
}

async function signInWithGoogle() {
    if (!firebaseAuthInstance) {
        mostrarAlerta('Firebase Auth no está inicializado.', 'error');
        return null;
    }

    const provider = new firebase.auth.GoogleAuthProvider();
    provider.setCustomParameters({ prompt: 'select_account' });

    try {
        const result = await firebaseAuthInstance.signInWithPopup(provider);
        const user = result.user;
        const idToken = await user.getIdToken();
        return { user, idToken };
    } catch (error) {
        console.error('Error en Firebase Google Sign-In:', error);
        throw new Error(error.message || 'No se pudo iniciar sesión con Google.');
    }
}

async function verificarUsuarioBackend(idToken) {
    const respuesta = await fetch('http://127.0.0.1:5000/api/verificar-usuario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idToken })
    });
    return respuesta.json();
}

async function registrarUsuarioBackend(idToken, usuarioDatos) {
    const respuesta = await fetch('http://127.0.0.1:5000/api/registro-usuario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idToken, ...usuarioDatos })
    });
    const data = await respuesta.json();
    return { ok: respuesta.ok, data };
}

function mostrarAlerta(mensaje, tipo = 'info', duracion) {
    const durPorDefecto = tipo === 'success' ? 7000 : 4500;
    const dur = typeof duracion === 'number' ? duracion : durPorDefecto;

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
    }, dur);
}

window.alert = (mensaje) => mostrarAlerta(String(mensaje), 'info');

initializeFirebaseAuth();

function Registro() {
    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";
    
    const VentanaRegistro = document.createElement("div");
    VentanaRegistro.className = "ventana-registro";
    
    // Lista local para manejar los intereses seleccionados de forma interactiva
    let interesesSeleccionados = [];
    
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
        
        <p style="font-size: 0.9rem; color: #64748b; margin-top: 15px; margin-bottom: 8px; font-weight: 600;">Áreas de Interés Literario:</p>
        <div class="intereses-seleccion" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 6px; margin-bottom: 20px;">
            <div class="interes-chip" data-interes="Matemáticas" style="padding: 6px; background: #f1f5f9; border: 2px solid #e2e8f0; border-radius: 99px; font-size: 0.8rem; text-align: center; cursor: pointer; font-weight: 600; color: #475569; transition: all 0.2s; user-select: none;">Matemáticas</div>
            <div class="interes-chip" data-interes="Tecnología" style="padding: 6px; background: #f1f5f9; border: 2px solid #e2e8f0; border-radius: 99px; font-size: 0.8rem; text-align: center; cursor: pointer; font-weight: 600; color: #475569; transition: all 0.2s; user-select: none;">Tecnología</div>
            <div class="interes-chip" data-interes="Ciencia Ficción" style="padding: 6px; background: #f1f5f9; border: 2px solid #e2e8f0; border-radius: 99px; font-size: 0.8rem; text-align: center; cursor: pointer; font-weight: 600; color: #475569; transition: all 0.2s; user-select: none;">Ciencia Ficción</div>
            <div class="interes-chip" data-interes="Fantasía" style="padding: 6px; background: #f1f5f9; border: 2px solid #e2e8f0; border-radius: 99px; font-size: 0.8rem; text-align: center; cursor: pointer; font-weight: 600; color: #475569; transition: all 0.2s; user-select: none;">Fantasía</div>
            <div class="interes-chip" data-interes="Misterio" style="padding: 6px; background: #f1f5f9; border: 2px solid #e2e8f0; border-radius: 99px; font-size: 0.8rem; text-align: center; cursor: pointer; font-weight: 600; color: #475569; transition: all 0.2s; user-select: none;">Misterio</div>
            <div class="interes-chip" data-interes="Aventura" style="padding: 6px; background: #f1f5f9; border: 2px solid #e2e8f0; border-radius: 99px; font-size: 0.8rem; text-align: center; cursor: pointer; font-weight: 600; color: #475569; transition: all 0.2s; user-select: none;">Aventura</div>
            <div class="interes-chip" data-interes="Historia" style="padding: 6px; background: #f1f5f9; border: 2px solid #e2e8f0; border-radius: 99px; font-size: 0.8rem; text-align: center; cursor: pointer; font-weight: 600; color: #475569; transition: all 0.2s; user-select: none;">Historia</div>
            <div class="interes-chip" data-interes="Romance" style="padding: 6px; background: #f1f5f9; border: 2px solid #e2e8f0; border-radius: 99px; font-size: 0.8rem; text-align: center; cursor: pointer; font-weight: 600; color: #475569; transition: all 0.2s; user-select: none;">Romance</div>
            <div class="interes-chip" data-interes="No Ficción" style="padding: 6px; background: #f1f5f9; border: 2px solid #e2e8f0; border-radius: 99px; font-size: 0.8rem; text-align: center; cursor: pointer; font-weight: 600; color: #475569; transition: all 0.2s; user-select: none;">No Ficción</div>
        </div>

        <button id="btn-enviar-registro" class="btn-iniciar-sesion">Finalizar Registro</button>
    </div>`;

    overlay.appendChild(VentanaRegistro);
    document.body.appendChild(overlay);

    // Lógica de clic interactivo para cambiar estilos y guardar intereses en el arreglo local
    VentanaRegistro.querySelectorAll('.interes-chip').forEach(chip => {
        chip.onclick = () => {
            const tema = chip.dataset.interes;
            if (interesesSeleccionados.includes(tema)) {
                // Si ya estaba seleccionado, se remueve del arreglo y vuelve a su estilo original
                interesesSeleccionados = interesesSeleccionados.filter(i => i !== tema);
                chip.style.background = "#f1f5f9";
                chip.style.color = "#475569";
                chip.style.borderColor = "#e2e8f0";
            } else {
                // Si no estaba, se agrega al arreglo y cambia a un color azul llamativo
                interesesSeleccionados.push(tema);
                chip.style.background = "#3b46c4"; 
                chip.style.color = "#ffffff";
                chip.style.borderColor = "#3b46c4";
            }
        };
    });

    const divGoogle = VentanaRegistro.querySelector('#div-google');
    const divSeccionRegistro = VentanaRegistro.querySelector('#seccion-registro');
    const divLogin = VentanaRegistro.querySelector('#contenedor-login');

    const currentUser = firebaseAuthInstance?.currentUser;
    if (currentUser) {
        if (divGoogle) divGoogle.style.display = 'none';
        if (divSeccionRegistro) {
            divSeccionRegistro.style.display = 'block';
            const h2 = divSeccionRegistro.querySelector('h2');
            if (h2) h2.innerText = `Hola, ${currentUser.displayName}`;
        }
        if (divLogin) divLogin.style.display = 'none';
        currentUser.getIdToken().then(token => {
            window.currentFirebaseIdToken = token;
        }).catch(() => {});
    }

    VentanaRegistro.querySelector('#google-login-btn').onclick = async () => {
        if (window.location.protocol === 'file:') {
            mostrarAlerta('Debes abrir la página mediante HTTP local (por ejemplo http://localhost:8000), no con file://.', 'error');
            return;
        }

        divLogin.style.display = 'none';
        divGoogle.style.display = 'block';

        try {
            const result = await signInWithGoogle();
            if (!result) {
                throw new Error('No se completó la autenticación de Google.');
            }

            const { user, idToken } = result;
            const backend = await verificarUsuarioBackend(idToken);

            if (backend.existe) {
                mostrarAlerta(`Bienvenido de vuelta, ${backend.usuario.nombre}`, 'success');
                localStorage.setItem('bibliotecaUsuario', JSON.stringify(backend.usuario));
                document.body.removeChild(overlay);
                window.location.reload();
                return;
            }

            divGoogle.style.display = 'none';
            divSeccionRegistro.style.display = 'block';
            const h2 = divSeccionRegistro.querySelector('h2');
            if (h2) h2.innerText = `Hola, ${user.displayName}`;
            window.currentFirebaseIdToken = idToken;
        } catch (error) {
            console.error('Error al iniciar sesión con Google:', error);
            divGoogle.style.display = 'none';
            divLogin.style.display = 'block';
            mostrarAlerta(error.message || 'No se pudo iniciar sesión con Google.', 'error');
        }
    };

    VentanaRegistro.querySelector('#btn-enviar-registro').onclick = async () => {
        const user = firebaseAuthInstance?.currentUser;
        if (!user) {
            mostrarAlerta('Debes iniciar sesión con Google antes de finalizar el registro.', 'error');
            return;
        }

        const cedula = VentanaRegistro.querySelector('#reg-cedula').value.trim();
        const rol = VentanaRegistro.querySelector('#reg-rol').value;
        const anio = VentanaRegistro.querySelector('#reg-anio').value;

        if (!cedula || !rol || !anio) {
            mostrarAlerta('Por favor, rellena todos los campos antes de finalizar.', 'error');
            return;
        }

        try {
            const idToken = window.currentFirebaseIdToken || await user.getIdToken(true);
            
            // Enviamos los datos al endpoint agregando el campo de intereses
            const respuesta = await registrarUsuarioBackend(idToken, {
                cedula,
                rol,
                anio_seccion: anio,
                name: user.displayName,
                email: user.email,
                picture: user.photoURL,
                intereses: interesesSeleccionados // <-- Pasados correctamente al backend
            });

            if (respuesta.ok) {
                mostrarAlerta('¡Registro exitoso! Perfil creado correctamente.', 'success');
                localStorage.setItem('bibliotecaUsuario', JSON.stringify(respuesta.data.usuario));
                document.body.removeChild(overlay);
                window.location.reload();
                return;
            }

            mostrarAlerta(`Error en el sistema: ${respuesta.data.error || respuesta.data.mensaje}`, 'error');
        } catch (error) {
            console.error('Error al conectar con el backend:', error);
            mostrarAlerta('Hubo un problema de red al procesar tu cuenta.', 'error');
        }
    };

    VentanaRegistro.querySelector('.btn-cerrar').onclick = () => document.body.removeChild(overlay);
    overlay.onclick = (e) => {
        if (e.target === overlay) document.body.removeChild(overlay);
    };
}

const botonLogin = document.querySelector('.btn-registro');
if (botonLogin) {
    botonLogin.onclick = (e) => {
        e.preventDefault();
        Registro();
    };
}