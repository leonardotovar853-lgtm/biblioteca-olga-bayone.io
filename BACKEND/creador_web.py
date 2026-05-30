from admin_datos import limpieza_datos
import os
import json

def clasificar_tarjetas(biblioteca):
    
    tarjetas_catalogo = []
    tarjetas_repositorio = []
    
    for libro in biblioteca.lista_libros:
        tipo_normalizado = libro.tipo.strip().lower()
        html_targeta = libro.generar_tarjeta_html()
            
        if tipo_normalizado == 'tesis':
                tarjetas_repositorio.append(html_targeta)
        else:
                tarjetas_catalogo.append(html_targeta)
                
    return tarjetas_catalogo, tarjetas_repositorio


def crear_web(biblioteca):
    try:
        # --- 1. CLASIFICACIÓN DE TARJETAS ---
        tarjetas_catalogo, tarjetas_repositorio = clasificar_tarjetas(biblioteca)
        
        libros_data = biblioteca.exportar_libros()
        tesis_data = biblioteca.exportar_tesis()
        
        # --- 2. PLANTILLAS HTML ---
        html_inicio_catalogo = """
<!DOCTYPE html>
<html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Catálogo de Libros</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" integrity="sha512-..." crossorigin="anonymous" referrerpolicy="no-referrer" />
        <link rel="stylesheet" href="../css/estilos.css">
        <link rel="stylesheet" href="../css/catalogo.css">
        <link rel="stylesheet" href="../css/banners.css">
        <link rel="stylesheet" href="../css/libros.css">
        <link rel="stylesheet" href="../css/accesoArea.css">
        <link rel="icon" href="../logo_olga_bayone.png">
    </head>
    <body>
        <nav id="menu" class="nav-menu">
            <div class="nav-content">
                <img class="logo_olga" src="../logo_olga_bayone.png" alt="logo_olga_bayone">
                <h1 class="title">Biblioteca Olga Bayone</h1>

                <button class="menu-toggle" id="menu-toggle" aria-label="Abrir Menu">
                    <span class="bar"></span>
                    <span class="bar"></span>
                    <span class="bar"></span>
                </button>

                <ul class="options">
                    <li><a class="op" href="index.html"><i class="fa-solid fa-house"></i> Inicio</a></li>
                    <li><a class="op" href="catalogo.html"><i class="fa-solid fa-magnifying-glass"></i> Catálogo</a></li>
                    <li><a class='op' href="repositorio.html"><i class="fa-solid fa-book"></i> Repositorio</a></li>
                    <li><a class="op" href="agregar_libro.html"><i class="fa-solid fa-plus"></i> Agregar Libro</a></li>
                    <li><a class="op" href="sobre_proyecto.html"><i class="fa-solid fa-circle-info"></i> Sobre el Proyecto</a></li>
                    <li><a class="op" href="sobre_nosotros.html"><i class="fa-solid fa-people-group"></i> Nosotros</a></li>
                </ul>
            </div>
        </nav>
        <main>
            <section class = 'banner-catalogo'>
                <div class = 'contenido-banner'>
                    <h2 class="titulo_seccion">Explora nuestra colección</h2>
                    <p>Encuentra los libros en la Biblioteca Olga Bayone</p>
                    <div class="search-container">
                        <input type="search" id="buscador" placeholder="Busca tu libro por título, autor o materia...">
                        <select id="filtro-area">
                            <optgroup label="LIBROS POR MATERIA">
                                <option value="all">Todas las categorías</option>
                                <option value="Matemática">Matemáticas</option>
                                <option value="Castellano y Literatura">Castellano</option>
                                <option value="Ciencias Naturales (Física, Química y Biología general)">Ciencias Naturales</option>
                                <option value="Ciencias Sociales">Ciencias Sociales</option>
                                <option value="Historia">Historia</option>
                                <option value="Informática y Tecnologia">Informática y Tecnologia</option>
                                <option value="Ingles y otras lenguas">Ingles y otras Lenguas</option>
                                <option value="Arte y Patrimonio">Arte y Patrimonio</option>
                            </optgroup>
                        </select>
                        <select id="filtro-año">
                            <option value="all">Todos</option>
                            <option value="1er Año">1er Año</option>
                            <option value="2do Año">2do Año</option>
                            <option value="3er Año">3er Año</option>
                            <option value="4to Año">4to Año</option>
                            <option value="5to Año">5to Año</option>
                        </select>
                    </div>
                </div>
            </section>
            <section class="book-content">
                <div class="grid-libros">"""
                
        html_fin_catalogo = """
            </section>
            <section id="recomendaciones" style="display:none;">
                <h2>Recomendaciones Relacionadas</h2>
                <div class="grid-libros" id="grid-recomendaciones"></div>
            </section>
        </main>   
        <script>
            const librosData = """ + json.dumps(libros_data) + """;
        </script>
        <script src="../js/buscador.js"></script> 
        <script src="../js/accesoArea.js"></script>   
        <script src="../js/nav.js"></script>
        <script src="../js/stars.js"></script>
        <script src="../js/flipCard.js"></script>
    </body>
</html>"""
        
        html_inicio_repositorio = """
<!DOCTYPE html>
<html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Repositorio</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" integrity="sha512-..." crossorigin="anonymous" referrerpolicy="no-referrer" />
        <link rel="stylesheet" href="../css/estilos.css">
        <link rel="stylesheet" href="../css/catalogo.css">
        <link rel="stylesheet" href="../css/banners.css">
        <link rel="stylesheet" href="../css/libros.css">
        <link rel="stylesheet" href="../css/accesoArea.css">
        <link rel="icon" href="../logo_olga_bayone.png">
    </head>
    <body>
        <nav id="menu" class="nav-menu">
            <div class="nav-content">
                <img class="logo_olga" src="../logo_olga_bayone.png" alt="logo_olga_bayone">
                <h1 class="title">Biblioteca Olga Bayone</h1>

                <button class="menu-toggle" id="menu-toggle" aria-label="Abrir Menu">
                    <span class="bar"></span>
                    <span class="bar"></span>
                    <span class="bar"></span>
                </button>

                <ul class="options">
                    <li><a class="op" href="index.html"><i class="fa-solid fa-house"></i> Inicio</a></li>
                    <li><a class="op" href="catalogo.html"><i class="fa-solid fa-magnifying-glass"></i> Catálogo</a></li>
                    <li><a class='op' href="repositorio.html"><i class="fa-solid fa-book"></i> Repositorio</a></li>
                    <li><a class="op" href="agregar_libro.html"><i class="fa-solid fa-plus"></i> Agregar Libro</a></li>
                    <li><a class="op" href="sobre_proyecto.html"><i class="fa-solid fa-circle-info"></i> Sobre el Proyecto</a></li>
                    <li><a class="op" href="sobre_nosotros.html"><i class="fa-solid fa-people-group"></i> Nosotros</a></li>
                </ul>
            </div>
        </nav>
        <main>
            <section class = 'banner-catalogo'>
                <div class = 'contenido-banner'>
                    <h2 class="titulo_seccion">Explora nuestra colección</h2>
                    <p>Encuentra los libros en la Biblioteca Olga Bayone</p>
                    <div class="search-container">
                        <input type="search" id="buscador" placeholder="Busca Proyectos de Investigación...">
                        <select id="filtro-area">
                            <optgroup label="REPOSITORIO DE TESIS">
                                <option value="all">Todas las categorías</option>
                                <option value="Salud">Salud</option>
                                <option value="Educación">Educación</option>
                                <option value="Orientación Vocacional">Orientación Vocacional</option>
                                <option value="Tecnología">Tecnología (Tesis)</option>
                            </optgroup>
                        </select>
                    </div>
                </div>
            </section>
            <section class="book-content">
                <div class="grid-libros">"""
        
        html_fin_repositorio = """
            </section>
            <section id="recomendaciones" style="display:none;">
                <h2>Recomendaciones Relacionadas</h2>
                <div class="grid-libros" id="grid-recomendaciones"></div>
            </section>
        </main>
        <script>
            const librosData = """ + json.dumps(tesis_data) + """;
        </script>  
        <script src="../js/buscadorRepositorio.js"></script> 
        <script src="../js/nav.js"></script>
        <script src="../js/stars.js"></script>
    </body>
</html>"""
        html_recomendaciones = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Biblioteca Olga Bayone</title>
    <link rel="icon" href="../logo_olga_bayone.png">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" integrity="sha512-..." crossorigin="anonymous" referrerpolicy="no-referrer" />
    <link rel="stylesheet" href="../css/estilos.css">
    <link rel="stylesheet" href="../css/banners.css">
    <link rel="stylesheet" href="../css/libros.css">
    <link rel="stylesheet" href="../css/accesoArea.css">
    <link rel="stylesheet" href="../css/catalogo.css">
    <script src="https://accounts.google.com/gsi/client" async defer></script>
</head>
<body>
    <nav id = "menu" class="nav-menu">
        <div class="nav-content">
            <div class="logo-title">
                <img class="logo_olga" src="../logo_olga_bayone.png" alt="logo_olga_bayone">
                <h1 class="title">Biblioteca Olga Bayone</h1>
            </div>

            <button class="menu-toggle" id="menu-toggle" aria-label="Abrir Menu">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
            </button>

            <ul class="options">
                <li><a class="op" href="index.html"><i class="fa-solid fa-house"></i> Inicio</a></li>
                <li><a class="op" href="catalogo.html"><i class="fa-solid fa-magnifying-glass"></i> Catálogo</a></li>
                <li><a class='op' href="repositorio.html"><i class="fa-solid fa-book"></i> Repositorio</a></li>
                <li><a class="op" href="agregar_libro.html"><i class="fa-solid fa-plus"></i> Agregar Libro</a></li>
                <li><a class="op" href="sobre_proyecto.html"><i class="fa-solid fa-circle-info"></i> Sobre el Proyecto</a></li>
                <li><a class="op" href="sobre_nosotros.html"><i class="fa-solid fa-people-group"></i> Nosotros</a></li>
            </ul>
        </div>
    </nav>
    
    <main class="main-content">
        <section class="banner-hero">
            <div class="banner-overlay">
                <div class="banner-info">
                    <h2>Bienvenido a la Biblioteca Digital Olga Bayone</h2>
                    <hr class="separador">
                    <p>Tu puerta al conocimiento, disponible en cualquier momento y lugar.</p>
                    <div class="botones-banner">
                        <a href="catalogo.html" class="btn-primario"><i class="fa-solid fa-magnifying-glass"></i>Explorar Libros</a>
                        <a href="sobre_proyecto.html" class="btn-secundario"><i class="fa-solid fa-circle-info"></i>Más Información</a>
                        <a class="btn-registro">Iniciar Seccion</a>
                    </div>
                </div>
            </div>
        </section>
        <section class="recommend-section" id="recomendaciones">
            <h2>Coleciones Destacadas</h2>
            <div class="grid-recomendaciones">

            </div>
        </section>
        <section class="area-content">
            <h2>Busca en Nuestras Areas Disponibles</h2>
            <ul class="list-area">
                <li>
                    <a href="catalogo.html?area=Matemática" class="boton-area">
                        <span class="icono icono-matematica"></span> 
                        <h3>Matemáticas</h3>
                    </a>
                </li>
                
                <li>
                    <a href="catalogo.html?area=Castellano y Literatura" class="boton-area">
                        <span class="icono icono-castellano"></span>
                        <h3>Castellano y Literatura</h3>
                    </a>
                </li>
                
                <li>
                    <a href="catalogo.html?area=Ciencias Naturales (Física, Química y Biología general)" class="boton-area">
                        <span class="icono icono-naturales"></span>
                        <h3>Ciencias Naturales</h3>
                    </a>
                </li>
                
                <li>
                    <a href="catalogo.html?area=Ciencias Sociales" class="boton-area">
                        <span class="icono icono-sociales"></span>
                        <h3>Ciencias Sociales</h3>
                    </a>
                </li>
                
                <li>
                    <a href="catalogo.html?area=Historia" class="boton-area">
                        <span class="icono icono-historia"></span>
                        <h3>Historia</h3>
                    </a>
                </li>

                <li>
                    <a href="catalogo.html?area=Informática y Tecnologia" class="boton-area">
                        <span class="icono icono-informatica"></span>
                        <h3>Informática y Tecnología</h3>
                    </a>
                </li>

                <li>
                    <a href="catalogo.html?area=Arte y Patrimonio" class="boton-area">
                        <span class="icono icono-arte"></span>
                        <h3>Arte y Patrimonio</h3>
                    </a>
                </li>
                <li>
                    <a href="catalogo.html?area=Ingles y otras lenguas" class="boton-area">
                        <span class="icono icono-ingles"></span>
                        <h3>Ingles y otras Lenguas</h3>
                    </a>
                </li>
                <li>
                    <a href="repositorio.html" class="boton-area">
                        <span class="icono icono-tesis"></span>
                        <h3>Tesis de Grado</h3>
                    </a>
                </li>
            </ul>
        </section>
    </main>
    <footer>
        <p>&copy; 2026 Biblioteca Digital Olga Bayone. Todos los derechos reservados.</p>
    </footer>
    <script>
        const librosData = """ + json.dumps(libros_data) + """;
    </script>
    <script src="../js/Registro.js"></script>
    <script src="../js/recomendacionInicio.js"></script>
    <script src="../js/nav.js"></script>
    <script src="../js/stars.js"></script>
</body>
</html>"""

        # --- 3. ESCRITURA FINAL ---
        base_dir = r'C:\Users\NEW DELL\Documents\PROGRAMACIÓN\PROYECTO_BIBLIOTECA_DIGITAL\FRONTEND'
        os.makedirs(base_dir, exist_ok=True)
        
        # Generar catálogo completo
        tarjetas_html_catalogo = ''.join(tarjetas_catalogo)
        html_completo_catalogo = html_inicio_catalogo + tarjetas_html_catalogo + html_fin_catalogo
        ruta_catalogo = os.path.join(base_dir, 'html','catalogo.html')
        with open(ruta_catalogo, 'w', encoding='utf-8') as f:
            f.write(html_completo_catalogo)
        print(f"✅ Archivo escrito: {ruta_catalogo}")
        
        # Generar repositorio completo
        tarjetas_html_repositorio = ''.join(tarjetas_repositorio)
        html_completo_repositorio = html_inicio_repositorio.replace('{pagina}', 'Repositorio') + tarjetas_html_repositorio + html_fin_repositorio
        ruta_repositorio = os.path.join(base_dir, 'html','repositorio.html')
        with open(ruta_repositorio, 'w', encoding='utf-8') as f:
            f.write(html_completo_repositorio)
        print(f"✅ Archivo escrito: {ruta_repositorio}")
        
        # Generar página de inicio con recomendaciones
        html_recomendaciones_completp = html_recomendaciones  # Ejemplo: primeras 1000 chars de recomendaciones
        ruta_inicio = os.path.join(base_dir, 'html','index.html')
        with open(ruta_inicio, 'w', encoding='utf-8') as f:
            f.write(html_recomendaciones_completp)

        num_catalogo = len(tarjetas_catalogo)
        num_repositorio = len(tarjetas_repositorio)
        print(f"✨ ¡Generación completada! Catálogo: {num_catalogo} libros, Repositorio: {num_repositorio} tesis.")
        
    except Exception as e:
        print(f'❌ Error al generar la web: {e}')

# --- EJECUCIÓN PRINCIPAL ---
def ejecucion_final():
# 1. Llamamos a limpieza_datos(). 
# Esta función ya hace el Paso 1 (Cargar), Paso 2 (Limpiar) y Paso 3 (Crear Objetos).
    try:
        biblioteca_final = limpieza_datos() 

        # 2. Si la biblioteca se creó correctamente, generamos la web
        if biblioteca_final is not None:
            crear_web(biblioteca_final)
            print("🚀 PROCESO COMPLETADO: Web actualizada con éxito.")
            return True
        else:
            print("❌ ERROR: No se pudo procesar la información de la nube.")
            return False
    except Exception as e:
        print(f'ERROR: {e}')
        return False
    
