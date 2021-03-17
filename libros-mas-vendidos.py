import requests
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd


def get_all_best_sellers_100():
    #Se recorren las paginas de los libros mas vendidos de la 1 a la 10
        datos = []
        for page_number in range(1,11):
            print('A continuación se muestran los libros de la página '+ str(page_number) + '\n')
            actual_datos = get_main_news(page_number)
            
            for libro_mas_vendidos in actual_datos:
                datos.append(libro_mas_vendidos)
                get_book_page_data(libro_mas_vendidos['url'])
                print('=================================')
                print(libro_mas_vendidos)
                print('=================================')
                print('\n')
                
        return datos

            
            
        
# La función get_main_news retornará un diccionario con todas las urls, títulos y autor de libros encontrados en la sección principal.
def get_main_news(page_number):
    url = 'https://www.todostuslibros.com/mas_vendidos?page='+str(page_number)

    respuesta = launch_request(url)

    contenido_web = BeautifulSoup(respuesta.text, 'html.parser')

# Buscar la etiqueta ul, que tenga la clase books, que es la lista que contiene todas las urls. 
    libreria = contenido_web.find('ul', attrs={'class':'books'})
# Con el resultado de esa búsqueda, utilizaremos findChildren para encontrar todos los divs que usen la clase que book-details que es la que contiene la url, el título y el autor,
# esto nos devolverá una lista con todos los resultados encontrados.
    libros = libreria.findChildren('div', attrs={'class':'book-details'})

# Después recorreremos la lista para obtener la url, el título, para ello usaremos el siguiente código:
    datos = [];
    for libro in libros:
        datos.append({
            'url': libro.find('h2').a.get('href'),
			'titulo': libro.find('h2').get_text().strip(),
			'autor': libro.find('h3').get_text().strip()
        })

    return datos


#Consigue la informacion relativa a los libros: editorial, edicion ...
#Esta informacion se alade a la ya obtenida de url, titulo y autor
def get_book_page_data(book_url):
    respuesta = launch_request(book_url)
    
    contenido_web = BeautifulSoup(respuesta.text, 'html.parser')
      
    data = {'materias': contenido_web.select_one('.materias a').get_text()}
    
    #Obtenemos las dos columnas de informacion con editorial, peso del libro y otros atributos
    informacion_relativa_libro = contenido_web.select('.col-12.col-sm-12.col-md-12.col-lg-6 > .row')
  
    for informacion_relativa_libro_i in informacion_relativa_libro:
        keys = informacion_relativa_libro_i.find_all('dt')
        values = informacion_relativa_libro_i.find_all('dd')
        
        for i in range(0,len(keys)):
            data[keys[i].get_text()] = values[i].get_text()
            
    
    print(data)
    return data
        
    
def launch_request(url):
    try:
        respuesta = requests.get(
            url,
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
            }
        )
        respuesta.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    return respuesta


if __name__ == '__main__':
    datos = get_all_best_sellers_100()
    df = pd.DataFrame(datos)
    print(df)
  
    # creación en excel en la raíz de usuario
    df.to_excel('libros_mas_vendidos.xlsx')
    df.to_csv('libros_mas_vendidos.csv')

   
