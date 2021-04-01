import requests
from bs4 import BeautifulSoup
import threading
import timeit
import csv
import os
import pandas as pd
            
        
# La función get_main_news retornará un diccionario con todas las urls, títulos y autor de libros encontrados en la sección principal.
def get_all_best_sellers_100():
    
    data_100 = [];
    barrier = threading.Barrier(11)
    
    for page_number in range(1,11):
        x = threading.Thread(target=get_bestsellerspage, args=(page_number,data_100,barrier))
        x.start();
    barrier.wait()
    return data_100

def get_bestsellerspage(page_number,data_100,barrier):
    url = 'https://www.todostuslibros.com/mas_vendidos?page='+str(page_number)
    respuesta = launch_request(url)

    contenido_web = BeautifulSoup(respuesta.text, 'html.parser')
    libreria = contenido_web.find('ul', attrs={'class':'books'})
    libros = libreria.findChildren('div', attrs={'class':'book-details'})

    # Después recorreremos la lista para obtener la url, el título, para ello usaremos el siguiente código:
    
    puesto_del_libro = (page_number-1) * 10
    for libro in libros:            
        #Se suma uno al puesto del libro para que este listo para asignarse.
        puesto_del_libro+=1;
        
        respuesta = launch_request(libro.find('h2').a.get('href'))
        contenido_web = BeautifulSoup(respuesta.text, 'html.parser')
              
        datos = {
            'puesto': puesto_del_libro,
            'url': libro.find('h2').a.get('href'),
            'titulo': libro.find('h2').get_text().strip(),
            'autor': libro.select_one('.author > a').get_text().strip(),
            'materias': contenido_web.select_one('.materias a').get_text()
        }
        
        #Obtenemos las dos columnas de informacion acerca editorial, peso del libro y otros atributos
        informacion_relativa_libro = contenido_web.select('.col-12.col-sm-12.col-md-12.col-lg-6 > .row')
            
        for informacion_relativa_libro_i in informacion_relativa_libro:
            keys = informacion_relativa_libro_i.find_all('dt')
            values = informacion_relativa_libro_i.find_all('dd')

            for i in range(0,len(keys)):
                datos[keys[i].get_text()] = values[i].get_text()
        
        #Evitamos condición de carrera ya que append es threadsafe porque es una operación atomica.
        data_100.append(datos)  
        
        #print('=================================')
        #print(datos)
        #print('=================================')
        #print('\n')
    barrier.wait();
   
            
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
        print(err)
        raise SystemExit(err)

    return respuesta


if __name__ == '__main__':
    start = timeit.default_timer()
    
    datos = get_all_best_sellers_100()
    df = pd.DataFrame(datos)
    #print(df)
  
    # creación en excel en la raíz de usuario
    df.to_excel('libros_mas_vendidos.xlsx',index=False)
    df.to_csv('libros_mas_vendidos.csv',index=False)
    
    stop = timeit.default_timer()
    print('Time: ', stop - start)
    print('\n' + 'Finish !')

   