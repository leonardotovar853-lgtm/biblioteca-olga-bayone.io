// Llamar a la función para mostrar los mejores libros al cargar la página
document.addEventListener('DOMContentLoaded', mostrarRecomendacionesInicio);

window.addEventListener('resize', mostrarRecomendacionesInicio);

function extraerValorNumerico(libro, claves) {
    for (const clave of claves) {
        const valor = Number(libro?.[clave]);
        if (Number.isFinite(valor) && valor >= 0) return valor;
    }
    return 0;
}

function obtenerPuntajeLibro(libro) {
    const anio = Number.parseInt(libro?.anio_publicacion || libro?.anio || 0, 10) || 0;
    const likes = extraerValorNumerico(libro, ['likes', 'likes_count', 'like_count', 'me_gusta', 'contador_likes', 'votos']);
    const tienePortada = Boolean(libro?.link_portada && /https?:|data:image/i.test(libro.link_portada));
    const tieneEnlace = Boolean(libro?.link && /https?:/i.test(libro.link));
    const tipoPeso = {
        Libro: 1.4,
        Tesis: 1.2,
        Guia: 1.1,
        Video: 1.0,
        Web: 1.0
    }[libro?.tipo] || 1;

    return (anio * 0.7) + (likes * 6) + (tienePortada ? 12 : 0) + (tieneEnlace ? 10 : 0) + tipoPeso;
}

function obtenerMejoresLibros(cantidad) {
    return librosData
        .filter(libro => !libro?.estado || libro.estado === 'Aprobado' || libro.estado === 'aprobado')
        .filter(libro => libro?.titulo && libro?.link)
        .map(libro => ({ ...libro, _score: obtenerPuntajeLibro(libro) }))
        .sort((a, b) => {
            if (b._score !== a._score) return b._score - a._score;
            const anioA = Number.parseInt(a?.anio_publicacion || a?.anio || 0, 10) || 0;
            const anioB = Number.parseInt(b?.anio_publicacion || b?.anio || 0, 10) || 0;
            if (anioB !== anioA) return anioB - anioA;
            return (a?.titulo || '').localeCompare(b?.titulo || '');
        })
        .slice(0, cantidad);
}

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

    // Priorizar libros con mejor combinación de actualidad, enlaces, portada y likes
    const mejoresLibros = obtenerMejoresLibros(numLibros);

    if (mejoresLibros.length === 0) return;

    // Generar HTML para los mejores libros
    gridRec.innerHTML = '';
    mejoresLibros.forEach(libro => {
        const tipo = libro.tipo || 'Libro';
        const recursoId = libro.ID || libro.id || '';
        const portada = libro.link_portada && (libro.link_portada.startsWith('http://') || libro.link_portada.startsWith('https://') || libro.link_portada.startsWith('data:image'))
            ? libro.link_portada
            : (tipo === 'Libro'
                ? 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=80'
                : tipo === 'Tesis'
                    ? 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=900&q=80'
                    : tipo === 'Guia'
                        ? 'https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=900&q=80'
                        : tipo === 'Video'
                            ? 'https://images.unsplash.com/photo-1517602302552-471fe67acf66?auto=format&fit=crop&w=900&q=80'
                            : 'https://images.unsplash.com/photo-1516321497487-e288fb19713f?auto=format&fit=crop&w=900&q=80');

        const tarjeta = document.createElement('div');
        tarjeta.className = 'libro-card';
        tarjeta.setAttribute('data-category', `${libro.area} ${tipo}`);
        tarjeta.setAttribute('data-type', tipo);
        tarjeta.setAttribute('data-year', libro.nivel);
        tarjeta.setAttribute('libro-id', recursoId);
        tarjeta.innerHTML = `
            <img src="${portada}" alt="Portada de ${libro.titulo}" loading="lazy">
            <div class="badge-${tipo.toLowerCase()}">${tipo}</div>
            <h3>${libro.titulo}</h3>
            ${tipo === 'Libro' ? `<p class="autor-name">${libro.autor} | ${libro.editorial}</p>` : ''}
            ${tipo === 'Tesis' ? `<p class="autor-name">Autores: ${libro.autor}</p>` : ''}
            ${tipo === 'Guia' ? `<p class="autor-name">Autor: ${libro.autor}</p>` : ''}
            ${tipo === 'Video' ? `<p class="autor-name">Autor: ${libro.autor}</p><p class="autor-name">Duración: ${libro.duracion || ''}</p>` : ''}
            ${tipo === 'Web' ? `<p class="autor-name">Plataforma: ${libro.plataforma || ''}</p>` : ''}
            <p class="año-public">${tipo === 'Libro' ? `<b>${libro.anio_publicacion}</b>` : `Año: <b>${libro.anio_publicacion}</b>`}</p>
            <div class="card-footer">
                <button class="btn-flip">Ver Descripcion</button>
                <a href="${libro.link}" target="_blank" class="btn-leer"
                    ${tipo === 'Video' ? 'style="background-color: #ff0000; color: white;"' : ''}
                    ${tipo === 'Web' ? 'style="background-color: #0076d6; color: white;"' : ''}
                >
                    ${tipo === 'Guia' ? 'Descargar PDF' : tipo === 'Video' ? 'Ver Video' : tipo === 'Web' ? 'Visitar Sitio' : `Leer ${tipo}`}
                </a>
                <button class="btn-like" onclick="darLike('${recursoId}')">
                    <i class="fa-solid fa-heart"></i>
                    <span id="count-${recursoId}">0</span>
                </button>
            </div>
        `;
        gridRec.appendChild(tarjeta);
    });
    seccionRec.style.display = 'block';
}
