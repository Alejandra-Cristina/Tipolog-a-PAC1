import requests
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd
            
        
# La función get_main_news retornará un diccionario con todas las urls, títulos y autor de libros encontrados en la sección principal.
def get_all_best_sellers_100():
    
    data = [];
    for page_number in range(0,11):
        url = 'https://www.todostuslibros.com/mas_vendidos?page='+str(page_number)
        respuesta = launch_request(url)

        contenido_web = BeautifulSoup(respuesta.text, 'html.parser')
        libreria = contenido_web.find('ul', attrs={'class':'books'})
        libros = libreria.findChildren('div', attrs={'class':'book-details'})

        # Después recorreremos la lista para obtener la url, el título, para ello usaremos el siguiente código:
        for libro in libros:            
            
            respuesta = launch_request(libro.find('h2').a.get('href'))
            contenido_web = BeautifulSoup(respuesta.text, 'html.parser')
              
            datos = {
                'url': libro.find('h2').a.get('href'),
                'titulo': libro.find('h2').get_text().strip(),
                'autor': libro.find('h3').get_text().strip(),
                'materias': contenido_web.select_one('.materias a').get_text()
            }
            
            #Obtenemos las dos columnas de informacion con editorial, peso del libro y otros atributos
            informacion_relativa_libro = contenido_web.select('.col-12.col-sm-12.col-md-12.col-lg-6 > .row')
            
            for informacion_relativa_libro_i in informacion_relativa_libro:
                keys = informacion_relativa_libro_i.find_all('dt')
                values = informacion_relativa_libro_i.find_all('dd')

                for i in range(0,len(keys)):
                    datos[keys[i].get_text()] = values[i].get_text()
                    
            data.append(datos)  
            #print('=================================')
            #print(data)
            #print('=================================')
            #print('\n')
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
    #print(df)
  
    # creación en excel en la raíz de usuario
    df.to_excel('libros_mas_vendidos.xlsx',index=False)
    df.to_csv('libros_mas_vendidos.csv',index=False)

   