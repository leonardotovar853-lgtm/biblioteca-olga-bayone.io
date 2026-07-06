// Llamar a la función para mostrar los mejores libros al cargar la página
document.addEventListener('DOMContentLoaded', mostrarRecomendacionesInicio);

window.addEventListener('resize', mostrarRecomendacionesInicio);

// No mostrar sección de recomendaciones estáticas al cargar la página, se calcula según búsqueda dinámica
function mostrarRecomendacionesInicio() {
    const seccionRec = document.getElementById('recomendaciones');
    const gridRec = document.querySelector('.grid-recomendaciones');
    if (!seccionRec || !gridRec) return;

    let numLibros;
    const anchoPantalla = window.innerWidth;

    if (anchoPantalla < 480) {
        numLibros = 3; // Muy pocos en celulares pequeños
    } else if (anchoPantalla < 768) {
        numLibros = 4; // Cantidad moderada para tablets/móviles grandes
    } else {
        numLibros = 6; // Full capacidad para computadoras
    }

    // Ordenar libros por año de publicación descendente (más recientes primero) y tomar los top 3
    const mejoresLibros = librosData
        .sort((a, b) => parseInt(b.anio_publicacion) - parseInt(a.anio_publicacion))
        .slice(0, numLibros);

    if (mejoresLibros.length === 0) return;

    // Generar HTML para los mejores libros
    gridRec.innerHTML = '';
    mejoresLibros.forEach(libro => {
        const tarjeta = document.createElement('div');
        tarjeta.className = 'libro-card';
        tarjeta.setAttribute('data-category', `${libro.area} ${libro.tipo}`);
        tarjeta.setAttribute('data-year', libro.nivel);
        tarjeta.innerHTML = `
            <div class='libro-card' data-category='${libro.area}' data-type='${libro.tipo}' data-year='${libro.nivel}' libro-id='${libro.ID}'>
            <img src="${libro.link_portada}">
            <div class="badge-${libro.tipo.toLowerCase()}">${libro.tipo}</div>
            <h3>${libro.titulo}</h3>
            <p class="autor-name">${libro.autor} | ${libro.editorial}</p>
            <p class="año-public"><b>${libro.anio_publicacion}</b></p>
            
            <div class="card-footer">
                <button class="btn-flip">Ver Descricion</button>
                <a href="${libro.link}" target="_blank" class="btn-leer">Leer ${libro.tipo}</a>
                <button class="btn-like" onclick="darLike('${libro.ID}')">
                    ❤️ <span id="count-${libro.ID}">0</span>
                </button>
            </div>
        </div>
        `;
        gridRec.appendChild(tarjeta);
    });
    seccionRec.style.display = 'block';
    gridRec.style.display = 'flex';
    gridRec.style.justifyContent = 'center';
    gridRec.style.gap = '30px';
    gridRec.style.flexWrap = 'wrap';
}
