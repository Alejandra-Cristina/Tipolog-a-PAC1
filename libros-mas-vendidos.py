import requests
import csv
from bs4 import BeautifulSoup

if __name__ == '__main__':
    datos = get_main_news()

# La función get_main_news retornará un diccionario con todas las urls y títulos de libros encontrados en la sección principal.
def get_main_news():
    url = 'https://www.todostuslibros.com/mas_vendidos?page=1'

    respuesta = launch_request(url)

# En esta función lo que hacemos es usar la librería requests para realizar la petición que será de tipo get y a parte de la url le pasaremos por cabecera un user agent válido para evitar problemas de compatibilidad por parte de la web.


# Para ver el contenido utilizaremos text, aquí se guarda todo el html de la página.
print(respuesta.text)


# Una vez hecha la petición, vamos a extraer la información que nos interesa, para ello pasaremos todo el contenido de la respuesta a BeautifulSoup para que haga su magia.

contenido_web = BeautifulSoup(respuesta.text, 'lxml')


# Buscar la etiqueta ul, que tenga la clase books, que es la lista que contiene todas las urls. 
libreria = contenido_web.find('ul', attrs={'class':'books'})


# Con el resultado de esa búsqueda, utilizaremos findChildren para encontrar todos los divs que usen la clase que book-details que es la que contiene la url, el título y el autor, esto nos devolverá una lista con todos los resultados encontrados.

libros = libreria.findChildren('div', attrs={'class':'book-details'})

# Después recorreremos la lista para obtener la url, el título, para ello usaremos el siguiente código:


datos = [];

for libro in libros:
    print('=================================')
    print(libro.find('h2').a.get('href'))
    print(libro.find('h2').get_text())
    print('=================================')
    datos.append({
        'url': libro.find('h2').a.get('href'),
        'titulo': libro.find('h2').get_text(),
        'autor' : libro.find('h3').get_text()
    })

return datos

# Para obtener los datos que nos interesan buscaremos en la etiqueta h3 y los extraeremos usando a.get('href') para extraer el link y get_text() para extraer el texto.


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


# Directorio actual donde se encuentra el script
currentDir = os.path.dirname(__file__)
filename = "libros_mas_vendidos.csv"
filePath = os.path.join(currentDir , filename)


lista = []
cabecera = ["URL","TITULO","AUTOR"]
lista.append(cabecera)


with open(filePath, 'w', newline='') as csvFile:
  writer = csv.writer(csvFile)
  for datos in lista:
    writer.writerow(datos)