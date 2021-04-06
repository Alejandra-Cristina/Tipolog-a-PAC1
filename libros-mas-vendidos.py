import requests
from bs4 import BeautifulSoup
import threading
import random
import timeit
import csv
import os
import pandas as pd
            
        
# La función get_all_best_sellers_100 retornará un diccionario con todas las urls, títulos, autor ... 
# de los libros encontrados en la lista de más vendidos de la web todostuslibros.
#
# La seccion de los mas vendidos en todostuslibros esta formada por 10 paginas 
#que se obtienen pasando un parametro page al subdominio de mas_vendidos
def get_all_best_sellers_100():
    
    data_100 = [];
    #El barrier esta para que 
    #hasta que no se ha extraido la informacion de las 10 paginas que componen el ranking no se continue con la ejecución
    barrier = threading.Barrier(11)
    
    for page_number in range(1,11):
        x = threading.Thread(target=get_bestsellerspage, args=(page_number,data_100,barrier))
        x.start();
    barrier.wait()
    return data_100

#Añade al diccionario data_100 los datos de los 10 libros de la pagina que se pasa como parametro
def get_bestsellerspage(page_number,data_100,barrier):
    url = 'https://www.todostuslibros.com/mas_vendidos?page='+str(page_number)
    respuesta = launch_request(url)
 
    contenido_web = BeautifulSoup(respuesta.text, 'html.parser')
    libreria = contenido_web.find('ul', attrs={'class':'books'})
    libros = libreria.findChildren('div', attrs={'class':'book-details'})

    #Recorreremos la lista con la informacion de los libros (libros) para obtener la url, el título ... :
    
    puesto_del_libro = (page_number-1) * 10
    for libro in libros:            
        #Se suma uno al puesto del libro para que el valor esté actualizado.
        puesto_del_libro+=1;
        
        respuesta = launch_request(libro.find('h2').a.get('href'))
        contenido_web = BeautifulSoup(respuesta.text, 'html.parser')
              
        datos = {
            'Puesto': puesto_del_libro,
            'Url': libro.find('h2').a.get('href'),
            'Título': libro.find('h2').get_text().strip(),
            'Autor': libro.select_one('.author > a').get_text().strip(),
            'Materias': contenido_web.select_one('.materias a').get_text()
        }
        
        #Obtenemos las dos columnas de informacion acerca editorial, peso del libro y otros atributos
        informacion_relativa_libro = contenido_web.select('.col-12.col-sm-12.col-md-12.col-lg-6 > .row')
            
        for informacion_relativa_libro_i in informacion_relativa_libro:
            keys = informacion_relativa_libro_i.find_all('dt')
            values = informacion_relativa_libro_i.find_all('dd')

            for i in range(0,len(keys)):
                datos[keys[i].get_text().replace(':','')] = values[i].get_text()
        
        #Evitamos una posible condición de carrera ya que append es threadsafe porque es una operación atomica.
        data_100.append(datos)  
        
        #print('=================================')
        #print(datos)
        #print('=================================')
        #print('\n')
    barrier.wait();
   
#Devuelve un user-agent "aleatorio" de la lista definida
def random_User_Agent():
    userAgent_list = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
                      'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
                      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36']
    aux_user = userAgent_list[random.randint(0, len(userAgent_list)-1)]
    #print(aux_user)
    return aux_user

#Realiza una peticion GET sobre la url que se pasa como parámetro
def launch_request(url):
    try:
        respuesta = requests.get(
            url,
            headers = {
                'User-Agent': random_User_Agent()
            }
        )
        respuesta.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        raise SystemExit(err)

    return respuesta

#Funcion main
#Se obtiene el diccionario con toda la info de los 100 libros mas vendidos
#Se transforma en dataFrame y se genera un csv y xlsx
#Se imprime el tiempo que tardo en ejecutarse
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

   