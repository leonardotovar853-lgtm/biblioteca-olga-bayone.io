// MOTOR DE BÚSQUEDA Y FILTRADO SINCRONIZADO
// Proyecto: Biblioteca Digital Olga Bayone
// ==========================================

// 1. Capturamos los elementos de la interfaz (Nodos)
const inputBuscador = document.getElementById('buscador');
const menuMateria = document.getElementById('filtro-area');
const menuAnio = document.getElementById('filtro-año');
const menuTipo = document.getElementById('filtro-tipo');

// 2. Función Maestra de Filtrado (Lógica Booleana AND)
function aplicarFiltros() {
    // Obtenemos los valores actuales de los filtros
    const textoUsuario = inputBuscador.value.toLowerCase().trim();
    const materiaElegida = menuMateria ? menuMateria.value : "all";
    const anioElegido = menuAnio ? menuAnio.value : "all";
    const tipoElegido = menuTipo ? menuTipo.value : "all";

    // Seleccionamos todas las tarjetas de libros generadas por Python
    const tarjetas = document.querySelectorAll('.libro-card');

    tarjetas.forEach(tarjeta => {
        // Extraemos los metadatos de la tarjeta (manejamos vacíos por seguridad con || "")
        const textoLibro = tarjeta.textContent.toLowerCase();
        const materiaLibro = tarjeta.getAttribute('data-category') || "";
        const anioLibro = tarjeta.getAttribute('data-year') || "";
        const tipoLibro = tarjeta.getAttribute('data-type') || "";

        // --- CONDICIONES LÓGICAS ---
        
        // C1: ¿El texto escrito está en el título, autor o descripción?
        const coincideTexto = textoLibro.includes(textoUsuario);

        // C2: ¿La materia está dentro de los metadatos?
        const coincideMateria = (materiaElegida === "all" || materiaLibro.includes(materiaElegida));

        // C3: ¿El año coincide o se seleccionaron todos?
        const coincideAnio = (anioElegido === "all" || anioLibro === anioElegido);

        // C4: ¿El tipo coincide o se seleccionaron todos?
        const coincideTipo = (tipoElegido === "all" || tipoLibro === tipoElegido);

        // --- RESULTADO FINAL ---
        // El libro solo se muestra si cumple las CUATRO condiciones al mismo tiempo
        if (coincideTexto && coincideMateria && coincideAnio && coincideTipo) {
            tarjeta.style.display = "block";
            tarjeta.style.opacity = "1";
        } else {
            tarjeta.style.display = "none";
            tarjeta.style.opacity = "0";
        }
    });
    mostrarRecomendaciones(); // Actualizamos recomendaciones dinámicamente según resultados visibles
}

// 3. ESCUCHADORES DE EVENTOS (Activan el filtro en tiempo real)
if (inputBuscador) inputBuscador.addEventListener('input', aplicarFiltros);
if (menuMateria) menuMateria.addEventListener('change', aplicarFiltros);
if (menuAnio) menuAnio.addEventListener('change', aplicarFiltros);
if (menuTipo) menuTipo.addEventListener('change', aplicarFiltros);


// 4. Funciones de Recomendaciones
function recomendarSimilares(libro, todosLibros, limite = 3) {
    // Categoría/tema + palabras clave para refinar recomendaciones
    const baseTokens = (libro.titulo + ' ' + (libro.descripcion || '') + ' ' + libro.area).toLowerCase().match(/\w+/g) || [];
    const tokenSet = Array.from(new Set(baseTokens.filter(t => t.length > 3)));

    const puntuados = todosLibros
        .filter(l => l.titulo !== libro.titulo)
        .map(l => {
            let score = 0;
            if (l.area === libro.area) score += 50;
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
    gridRec.innerHTML = '';
    recomendaciones.forEach(libro => {
        const tarjeta = document.createElement('div');
        tarjeta.className = 'libro-card';
        tarjeta.setAttribute('data-category', `${libro.area} ${libro.tipo}`);
        tarjeta.setAttribute('data-year', libro.nivel);
        if (libro.tipo === "Libro") {
            tarjeta.innerHTML = `
            <div class='libro-card' data-category='${libro.area}' data-type='${libro.tipo}' data-year='${libro.nivel}' libro-id='${libro.id}'>
            <img src="${libro.link_portada}">
            <div class="badge-${libro.tipo.toLowerCase()}">${libro.tipo}</div>
            <h3>${libro.titulo}</h3>
            <p class="autor-name">${libro.autor} | ${libro.editorial}</p>
            <p class="año-public"><b>${libro.anio_publicacion}</b></p>
            
            <div class="card-footer">
                <button class="btn-flip">Ver Descricion</button>
                <a href="${libro.link}" target="_blank" class="btn-leer">Leer ${libro.tipo}</a>
                <button class="btn-like" onclick="darLike('${libro.id}')">
                    ❤️ <span id="count-${libro.id}">0</span>
                </button>
            </div>
        </div>
        `;
        }
        else if (libro.tipo === "Tesis") {
            tarjeta.innerHTML = `
            <div class='libro-card' data-category='${libro.area}' data-type='${libro.tipo}' data-year='${libro.nivel}' libro-id='${libro.id}'>
            <img src="${libro.link_portada}">
            <div class="badge-${libro.tipo.toLowerCase()}">${libro.tipo}</div>
            <h3>${libro.titulo}</h3>
            <p class="autor-name">Autores: ${libro.autor}</p>
            <p class="año-public">Tutor: ${libro.tutor} | Asesor metodológico: ${libro.asesor} | <b>${libro.anio_publicacion}</b></p>
            
            <div class="card-footer">
                <button class="btn-flip">Ver Descricion</button>
                <a href="${libro.link}" target="_blank" class="btn-leer">Leer ${libro.tipo}</a>
                <button class="btn-like" onclick="darLike('${libro.id}')">
                    ❤️ <span id="count-${libro.id}">0</span>
                </button>
            </div>
        </div>
            `;
        }
        else if (libro.tipo === "Guia") {
            tarjeta.innerHTML = `
            <div class='libro-card' data-category='${libro.area}' data-type='${libro.tipo}' data-year='${libro.nivel}' libro-id='${libro.id}'>
            <img src="${libro.link_portada}" alt="Portada de ${libro.titulo}">
            <div class="badge-${libro.tipo.toLowerCase()}">📄 ${libro.tipo}</div>
            <h3>${libro.titulo}</h3>
            <p class="autor-name">Autor: ${libro.autor}</p>
            <p class="año-public">Año: <b>${libro.anio_publicacion}</b></p>
            <p class="autor-name">Temas: ${libro.temas}</p>
            
            <div class="card-footer">
                <button class="btn-flip">Ver Descricion</button>
                <a href="${libro.link}" target="_blank" class="btn-leer">Descargar PDF</a>
                <button class="btn-like" onclick="darLike('${libro.id}')">
                    ❤️ <span id="count-${libro.id}">0</span>
                </button>
            </div>
        </div>
            `;
        }
        else if (libro.tipo === "Video") {
            tarjeta.innerHTML = `
            <div class='libro-card' data-category='${libro.area}' data-type='${libro.tipo}' data-year='${libro.nivel}' libro-id='${libro.id}'>
            <img src="${libro.link_portada}" alt="Portada de ${libro.titulo}">
            <div class="badge-${libro.tipo.toLowerCase()}">🎥 ${libro.tipo}</div>
            <h3>${libro.titulo}</h3>
            <p class="autor-name">Duración: ${libro.duracion}</p>
            <p class="año-public">Año: <b>${libro.anio_publicacion}</b></p>
            
            <div class="card-footer">
                <button class="btn-flip">Ver Descricion</button>
                <a href="${libro.link}" target="_blank" class="btn-leer" style="background-color: #ff0000; color: white;">Ver Video</a>
                <button class="btn-like" onclick="darLike('${libro.id}')">
                    ❤️ <span id="count-${libro.id}">0</span>
                </button>
            </div>
        </div>
            `;
        }

        else if (libro.tipo === "Web") {
            tarjeta.innerHTML = `
            <div class='libro-card' data-category='${libro.area}' data-type='${libro.tipo}' data-year='${libro.nivel}' libro-id='${libro.id}'>
            <img src="${libro.link_portada}">
            <div class="badge-${libro.tipo.toLowerCase()}">🌐 ${libro.tipo}</div>
            <h3>${libro.titulo}</h3>
            <p class="autor-name">Plataforma: ${libro.plataforma}</p>
            <p class="año-public">Año: <b>${libro.anio_publicacion}</b></p>
            
            <div class="card-footer">
                <button class="btn-flip">Ver Descricion</button>
                <a href="${libro.link}" target="_blank" class="btn-leer" style="background-color: #0076d6; color: white;">Visitar Sitio</a>
                <button class="btn-like" onclick="darLike('${libro.id}')">
                    ❤️ <span id="count-${libro.id}">0</span>
                </button>
            </div>
        </div>
            `;
        }
        gridRec.appendChild(tarjeta);
    });
    seccionRec.style.display = 'block';
    
}

// Mensaje de confirmación en consola para saber que todo cargó bien
console.log("Sistema de filtrado sincronizado y activo. Listo para procesar libros.");


