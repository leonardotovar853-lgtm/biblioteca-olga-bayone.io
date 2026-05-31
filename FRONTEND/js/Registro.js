// 1. Inicializamos Google una sola vez al cargar la página
google.accounts.id.initialize({
    client_id: "520347031267-ph0fosq8l2ngoinasnm4b914vnrbqk1k.apps.googleusercontent.com",
    ux_mode: 'popup',
    itp_support: true,
    callback: async (response) => {
        // Guardamos el token en memoria global
        window.googleCredential = response.credential;

        // Decodificación local solo para validar la visual del cliente
        const base64Url = response.credential.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join(''));
        const payload = JSON.parse(jsonPayload);
        
        window.datosGoogle = { 
            id: payload.sub, 
            given_name: payload.given_name,
            email: payload.email,
            picture: payload.picture
        };

        const divGoogle = document.querySelector('.ventana-registro #div-google');
        const divLogin = document.querySelector('.ventana-registro #contenedor-login');
        const divSeccionRegistro = document.querySelector('.ventana-registro #seccion-registro');

        // Permite pruebas tanto con la institucional como con Gmail en tu red local
        if (payload.email.endsWith('@olgabayone.com') || payload.email.endsWith('@gmail.com')) {
            try {
                // CORRECCIÓN 1: Enviamos la credencial completa para que Python la autentique con la API de Google
                const loginRespuesta = await fetch('http://localhost:5000/api/verificar-usuario', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ credential: response.credential }) 
                });
                const loginData = await loginRespuesta.json();

                // Si el servidor confirma que ya estabas registrado en el Sheets
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

            // Si es un usuario nuevo en la plataforma, desplegamos el formulario escolar
            if(divGoogle && divSeccionRegistro) {
                divGoogle.style.display = 'none';
                divSeccionRegistro.style.display = 'block';
                divSeccionRegistro.querySelector('h2').innerText = `Hola, ${payload.given_name}`;
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

// ... (Función Registro() intermedia se queda igual hasta el evento del botón enviar)

    // Botón Finalizar Registro
    VentanaRegistro.querySelector('#btn-enviar-registro').onclick = async () => {
        if (!window.googleCredential) {
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

        // CORRECCIÓN 2: Estructura exacta que espera tu lógica de Python
        const datosUsuario = {
            credential: window.googleCredential,
            cedula: cedula,
            rol: rol,
            anio_seccion: anio
        };

        try {
            const respuesta = await fetch('http://localhost:5000/api/registro-usuario', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datosUsuario)
            });

            const resultado = await respuesta.json();

            if (respuesta.ok) {
                alert(`¡Registro exitoso! Perfil creado correctamente.`);
                localStorage.setItem('bibliotecaUsuario', JSON.stringify(resultado.usuario));
                const overlayElem = document.querySelector('.modal-overlay');
                if (overlayElem) document.body.removeChild(overlayElem);
                window.location.reload();
            } else {
                // Captura los raise ValueError enviados por tus setters de Python (ej: Cédula inválida)
                alert(`Error en el registro: ${resultado.error}`);
            }
        } catch (error) {
            console.error("Error al conectar con el backend:", error);
            alert("Hubo un problema de red al procesar tu cuenta.");
        }
    };