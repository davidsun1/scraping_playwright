from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser
import re
import pandas as pd
import sqlite3
from funciones import extraer_apartados, iframe_url, split_string_primer_guion, split_string_dos_puntos

URL = "https://treball.barcelonactiva.cat/porta22/cat/assetsocupacio/ofertesfeina/ofertes-feina_v2.jsp"

if __name__ == '__main__':
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_load_state("networkidle")
        html = page.inner_html("body")

        # Pasear el archivo HTML con Selectolax
        tree = HTMLParser(html)
        # llamar funcion que devuelve lista de 8 apartados: comerç, Cultura i turisme...
        lista_apartados = extraer_apartados(tree)

        # llamada funcion que extrae strings de los iframes que luego se une al URL y crea los URLs de cada apartado
        lista_url = iframe_url(tree, URL)

    # unir los apartaods con sus respectivos URLs en un zip:
    result_dict = dict(zip(lista_apartados, lista_url))

    final_list = []  # lista que se irá guardando los elementos de interes

    for key, value in result_dict.items():
        with sync_playwright() as p:

            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(value)
            page.wait_for_load_state("networkidle")
            html = page.inner_html("body")
            tree = HTMLParser(html)

            combined_divs = []  # lista que guarda los divs de todas las paginas juntas
            # Seguir pulsando "Seguent" hasta que no se pueda
            while True:
                divs = tree.css('div[class="tc-job-list"] > div')
                combined_divs.extend(divs)
                # mirar si hay un Següent" boton para pulsar
                next_button = page.query_selector('li.rc-pagination-next:not(.rc-pagination-disabled)')
                if next_button:
                    next_button.click()
                    page.wait_for_load_state("networkidle")
                else:
                    break  # salida del loop si ya no hay boton

        for combined_div in combined_divs:
            # separar: "40317MKP - Cambrer/a de pisos (SB HOTELS)"
            part1, part2 = split_string_primer_guion(combined_div.css_first('a[class="tc-job-link"]').text())
            # ID: eliminar palabras y cast de string a int
            part1 = int(re.sub("[^0-9]", "", part1))
            # lugar
            location = combined_div.css_first('div[class="tc-job-cell tc-job-location"]').text()
            # mirar si hay null en sector he encontrado uno: 40026 - Rble. Botiga Gelats/Llet
            span_element = combined_div.css_first('span.tc-job-cell.tc-job-industry')
            # Check si el elemento span existe
            if span_element:
                industry_text = split_string_dos_puntos(span_element.text())
                if not industry_text:
                    industry_text = ""  # se asigna un string vacio si no hay nada

            date = combined_div.css_first('div.tc-job-cell.tc-job-date').text()
            link = combined_div.css_first('a[class="tc-job-link"]').attributes['href']

            attributos = {
                "id": part1,
                "apartado": key,
                "titulo": part2.strip(),
                "lugar": location,
                "sector": industry_text.strip(),
                "fecha": date,
                "link": link
            }
            final_list.append(attributos)

    # Crear un pandas DataFrame
    df = pd.DataFrame(final_list)

    # crear un csv a partir del pandas DF
    df.to_csv("data.csv", index=False)

    # crear un JSON a partir del pandas DF
    df.to_json("data.json", orient="records")

    # Conectar a SQLite database
    db_1 = sqlite3.connect('data.db')

    # pandas DataFrame a SQLite database
    df.to_sql('people', db_1, if_exists='replace', index=False)

    # cerrar conexion
    db_1.close()
