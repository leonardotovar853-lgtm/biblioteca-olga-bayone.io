// UNIFICADO: Captura de parámetros de la interfaz al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    // 1. Inicializamos el lector de parámetros de la URL
    const parametros = new URLSearchParams(window.location.search);
    const areaABuscar = parametros.get('area');
    const tipoDesdeBoton = parametros.get('tipo');

    console.log("🔍 Detectado en URL -> Área:", areaABuscar, "| Tipo:", tipoDesdeBoton);

    let requiereEspera = false;

    // 2. Procesamos el parámetro de ÁREA (Materia)
    if (areaABuscar) {
        const selectorArea = document.getElementById('filtro-area'); 
        if (selectorArea) {
            console.log("✅ Selector de área configurado");
            selectorArea.value = areaABuscar;
            requiereEspera = true; // Si viene de Sheets, necesitaremos esperar que cargue
        } else {
            console.error("❌ No encontré el elemento con ID 'filtro-area'.");
        }
    }

    // 3. Procesamos el parámetro de TIPO (Tesis, Guía, etc.)
    if (tipoDesdeBoton) {
        const menuTipo = document.getElementById('filtro-tipo');
        if (menuTipo) {
            console.log("✅ Selector de tipo configurado");
            menuTipo.value = tipoDesdeBoton;
            requiereEspera = true;
        } else {
            console.error("❌ No encontré el elemento con ID 'filtro-tipo'.");
        }
    }

    // 4. EJECUCIÓN DEL FILTRADO
    // Definimos una función interna para aplicar los filtros de forma segura
    const ejecutarFiltroSeguro = () => {
        if (typeof aplicarFiltros === "function") {
            console.log("🚀 Ejecutando aplicarFiltros()...");
            aplicarFiltros(); 
        } else {
            console.error("❌ La función aplicarFiltros no existe o no se ha cargado aún.");
        }
    };

    // Si la URL traía algún parámetro, le damos un margen de espera de 800ms
    // para asegurarnos de que Python / Sheets ya dibujaron las tarjetas en el HTML.
    if (requiereEspera) {
        setTimeout(ejecutarFiltroSeguro, 800);
    } else {
        // Si entró directo a la página normal sin tocar botones, filtramos de inmediato
        ejecutarFiltroSeguro();
    }
});