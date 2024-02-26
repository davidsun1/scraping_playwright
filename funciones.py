import csv

def extraer_apartados(tree):
    ul_tag = tree.css('ul[class="dv-eot-356"] > li > a')
    # iteramos en la lista. y extraemos el texto
    lista_apartados = []
    for ul in ul_tag:
        lista_apartados.append(ul.text())  # print(ul.text())

    return lista_apartados


# 2 Extraer los 8 URL de los iframes: (crea una lista con con objetos "node")
def iframe_url(tree, url):
    iframe_tags = tree.css('iframe')
    lista_url = []
    # extraer el valor del atributo src de los iframes anteriores
    for iframe in iframe_tags:
        url_final = url_conversor(url, iframe.attributes['src'])
        lista_url.append(url_final)

    return lista_url


# crear los URLs de los 8 apartados
def url_conversor(url_orig, suffix):

    # encuntra el ultimo index of '/'
    last_slash_index = url_orig.rfind('/')
    # Extrae la url y le añade '/'
    base_url = url_orig[:last_slash_index + 1]
    # añade la URL original
    final_url = base_url + suffix

    return final_url


def split_string_primer_guion(input_string):
    # separa string por le primer guion: "-"
    parts = input_string.split("-", 1)

    # retorna las partes separadas
    if len(parts) == 2:
        return parts[0], parts[1]
    else:
        # retonra nada si "-" no es encontrado
        return input_string, None

def split_string_dos_puntos(input_string):
    # separa string por le primer ":"
    parts = input_string.split(":", 1)

    return parts[1]
