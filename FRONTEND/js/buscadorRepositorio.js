
const inputBuscador = document.getElementById('buscador');
const menuMateria = document.getElementById('filtro-area');
const menuTipo = document.getElementById('filtro-tipo');
const parametros = new URLSearchParams(window.location.search);
const tipoDesdeBoton = parametros.get('tipo');
const areaDesdeBoton = parametros.get('area');

// Inicializa filtros desde la URL si están presentes
function inicializarFiltrosDesdeUrl() {
    let filtroAplicado = false;

    if (menuTipo && tipoDesdeBoton) {
        menuTipo.value = tipoDesdeBoton;
        filtroAplicado = true;
    }

    if (menuMateria && areaDesdeBoton) {
        menuMateria.value = areaDesdeBoton;
        filtroAplicado = true;
    }

    if (filtroAplicado) {
        setTimeout(aplicarFiltros, 100);
    }
}

// 2. Función Maestra de Filtrado (Lógica Booleana AND)
function aplicarFiltros() {
    // Obtenemos los valores actuales de los filtros
    const textoUsuario = inputBuscador ? inputBuscador.value.toLowerCase().trim() : "";
    const materiaElegida = menuMateria ? menuMateria.value : "all";
    const tipoElegido = menuTipo ? menuTipo.value : "all";

    // Seleccionamos todas las tarjetas de libros generadas por Python
    const tarjetas = document.querySelectorAll('.libro-card');

    tarjetas.forEach(tarjeta => {
        // Extraemos los metadatos de la tarjeta
        const textoLibro = tarjeta.textContent.toLowerCase();
        const materiaLibro = tarjeta.getAttribute('data-category');
        const tipoLibro = tarjeta.getAttribute('data-type') || "";

        // --- CONDICIONES LÓGICAS ---
        
        // C1: ¿El texto escrito está en el título, autor o descripción?
        const coincideTexto = textoLibro.includes(textoUsuario);

        // C2: ¿La materia está dentro de los metadatos?
        const coincideMateria = (materiaElegida === "all" || (materiaLibro || "").toLowerCase().includes(materiaElegida.toLowerCase()));

        // C3: ¿El tipo coincide o se seleccionaron todos?
        const coincideTipo = (tipoElegido === "all" || (tipoLibro || "").toLowerCase() === tipoElegido.toLowerCase());

        // --- RESULTADO FINAL ---
        // El libro solo se muestra si cumple todas las condiciones al mismo tiempo
        if (coincideTexto && coincideMateria && coincideTipo) {
            tarjeta.style.display = "block";
            // Pequeño efecto visual de entrada
            tarjeta.style.opacity = "1";
        } else {
            tarjeta.style.display = "none";
            tarjeta.style.opacity = "0";
        }
    });

    // Mostrar recomendaciones
    mostrarRecomendaciones();
}

// 3. Escuchadores de Eventos (Listeners)
// Cada vez que el usuario haga algo, la función se ejecuta automáticamente
if (inputBuscador) inputBuscador.addEventListener('input', aplicarFiltros);
if (menuMateria) menuMateria.addEventListener('change', aplicarFiltros);
if (menuTipo) menuTipo.addEventListener('change', aplicarFiltros);

// Inicia los filtros con parámetros URL cuando sea necesario
inicializarFiltrosDesdeUrl();

// 4. Funciones de Recomendaciones
function recomendarSimilares(libro, todosLibros, limite = 5) {
    // Categoría/tema + palabras clave para refinar recomendaciones
    const baseTokens = (libro.titulo + ' ' + (libro.descripcion || '') + ' ' + libro.area).toLowerCase().match(/\w+/g) || [];
    const tokenSet = Array.from(new Set(baseTokens.filter(t => t.length > 3)));

    const puntuados = todosLibros
        .filter(l => l.titulo !== libro.titulo)
        .map(l => {
            let score = 0;
            if (l.autor.toLowerCase() === libro.autor.toLowerCase()) score += 35;
            if (l.area === libro.area) score += 30;
            if (l.tipo === libro.tipo) score += 10;

            const anioBase = parseInt(libro.anio_publicacion);
            const anioLib = parseInt(l.anio_publicacion);
            if (!isNaN(anioBase) && !isNaN(anioLib)) {
                const diff = Math.abs(anioBase - anioLib);
                if (diff === 0) score += 8;
                else if (diff === 1) score += 4;
            }

            const texto = (l.titulo + ' ' + (l.descripcion || '') + ' ' + l.area).toLowerCase();
            tokenSet.forEach(token => { if (texto.includes(token)) score += 2; });

            return { libro: l, score };
        })
        .filter(item => item.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, limite)
        .map(item => item.libro);

    if (puntuados.length > 0) return puntuados;

    // Fallback suave por área y tipo si no hay coincidencias granulares
    return todosLibros.filter(l => l.area === libro.area || l.tipo === libro.tipo).slice(0, limite);
}

function mostrarRecomendaciones() {
    const textoUsuario = inputBuscador.value.toLowerCase().trim();
    const seccionRec = document.getElementById('recomendaciones');
    const gridRec = document.getElementById('grid-recomendaciones');
    if (!textoUsuario) {
        seccionRec.style.display = 'none';
        return;
    }
    // Encontrar libros visibles
    const tarjetasVisibles = Array.from(document.querySelectorAll('.libro-card')).filter(t => t.style.display === 'block');
    if (tarjetasVisibles.length === 0) {
        seccionRec.style.display = 'none';
        return;
    }
    // Tomar el primer libro visible y recomendar similares
    const primeraTarjeta = tarjetasVisibles[0];
    const titulo = primeraTarjeta.querySelector('h3').textContent;
    const libroBase = librosData.find(l => l.titulo === titulo);
    if (!libroBase) {
        seccionRec.style.display = 'none';
        return;
    }
    const recomendaciones = recomendarSimilares(libroBase, librosData);
    if (recomendaciones.length === 0) {
        seccionRec.style.display = 'none';
        return;
    }
    // Generar HTML para recomendaciones
    gridRec.innerHTML = "";
    recomendaciones.forEach(libro => {
        const tarjeta = document.createElement('div');
        tarjeta.className = 'libro-card';
        tarjeta.setAttribute('data-category', `${libro.area} ${libro.tipo}`);
        tarjeta.setAttribute('data-year', libro.nivel);
        tarjeta.innerHTML = `
            <img src="${libro.link_portada}" alt="Portada de ${libro.titulo}">
            <div class="badge-${libro.tipo.toLowerCase()}">${libro.tipo}</div>
            <h3>${libro.titulo}</h3>
            <p class="autor-name">${libro.autor}</p>
            <p class="año-public"><b>${libro.anio_publicacion}</b></p>
            <a href="${libro.link}" target="_blank" class="btn-leer">Leer ${libro.tipo}</a>
        `;
        gridRec.appendChild(tarjeta);
    });
    seccionRec.style.display = 'block';
}