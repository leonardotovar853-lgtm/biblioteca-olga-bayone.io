document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const areaABuscar = params.get('area');

    console.log("Intentando filtrar por:", areaABuscar); // Esto saldrá en F12

    if (areaABuscar) {
        // CAMBIA 'filtro-area' por el ID real de tu cuadrito de materias
        const selectorArea = document.getElementById('filtro-area'); 

        if (selectorArea) {
            console.log("Selector encontrado con éxito");
            selectorArea.value = areaABuscar;

            // Forzamos el filtrado después de un momento
            setTimeout(() => {
                if (typeof aplicarFiltros === "function") {
                    console.log("Ejecutando aplicarFiltros()...");
                    aplicarFiltros(); 
                } else {
                    console.error("La función aplicarFiltros no existe en esta página.");
                }
            }, 800); // Subimos a 800ms por si el Sheets es lento
        } else {
            console.error("No encontré ningún elemento con el ID 'filtro-area'. Revisa tu HTML.");
        }
    }
});