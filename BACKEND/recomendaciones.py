from admin_datos import limpieza_datos
from modelos import Biblioteca
import pandas

# Data Recursos
biblioteca = limpieza_datos()

def convertir_data(biblioteca):
    
    lista = [libro.to_dict() for libro in biblioteca.lista_libros]
    
    return lista


convertir_data(biblioteca)