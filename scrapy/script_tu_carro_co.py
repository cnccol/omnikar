#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 08:43:21 2019

@author: Edgar Federico Rivadeneira
"""

'''
scraping from: https://carros.tucarro.com.co/
'''

import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from os import listdir
import ast


''' 
el sitio web posee 42 paginas. Cada pagina tiene 48 resultados
Esta clase obtiene las urls de todos los artículos de cada página. 
Sobre esas urls luego se hace el scraping de la información que tiene cada producto
'''


class tu_carro_co:
    
    def __init__(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 15)
        self.driver.get('https://carros.tucarro.com.co/')
        self.list_urls = []

    def cambia_de_pagina(self, numero_pagina):
        path_pagina = 'https://carros.tucarro.com.co/' + '_Desde_' + str(numero_pagina)
        self.driver.get(path_pagina)
        
    def urls_de_una_pagina(self):
        ol_search_results = self.driver.find_element_by_id('searchResults')
        articles_list = ol_search_results.find_elements_by_xpath('./li[@class="results-item highlighted article grid "]')
        for article in articles_list:
            link_article_a = article.find_element_by_tag_name('a')
            url_articles = link_article_a.get_attribute('href')
            self.list_urls.append(url_articles)
            
   
########################################################
# se corre la primer clase y se obtienen las urls
     
# inicializa la clase:
class_tu_carro = tu_carro_co()
# busca urls de la primera pagina
class_tu_carro.urls_de_una_pagina()
numero_pagina = 49
for i in range(1,42):
    try:
        print(i)
        class_tu_carro.cambia_de_pagina(numero_pagina)
        class_tu_carro.urls_de_una_pagina()
        numero_pagina = numero_pagina + 48
    except Exception as e:
       print(i)
       print(e)
       numero_pagina = numero_pagina + 48
       pass
   
# resultado de la busqueda de urls de articulos
class_tu_carro.list_urls   
dict_urls_articulos = {'urls': class_tu_carro.list_urls }
df_urls_articulos = pd.DataFrame(dict_urls_articulos)
class_tu_carro.driver.quit()


#################################################


''' 
En la segunda parte del script se accede a la url de cada articulo y se descarga la informacion
Marca, placa, modelo, versión, precio, ubicación, Kilometros, imagenes
Se descarga 1 csv por cada artículo. Esto es para evitar cargar excesivamente la memoria de la computadora
'''

class articulo_tu_carro_co():
    
    def __init__(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 15)
     
        
    def inicia_articulo(self, url_articulo_in):
        self.driver.get(url_articulo_in)
        self.dict_datos = {}
        
        
    def obtiene_imagenes(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'gallery-content.item-gallery__wrapper')))
            gallery = self.driver.find_element_by_class_name('gallery-content.item-gallery__wrapper')
            list_imagenes_str = gallery.get_attribute('data-full-images')
            list_imagenes = ast.literal_eval(list_imagenes_str)
            self.imagenes_articulo = [dict_images['src'] for dict_images in list_imagenes]
            self.dict_datos['url_imagenes'] = [self.imagenes_articulo]
        except Exception as e:
            print(e)
            self.dict_datos['url_imagenes'] = ['NA']
        
        
    def datos_articulo(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'specs-list')))
            unordered_list_datos = self.driver.find_element_by_class_name('specs-list')
            listas_datos = unordered_list_datos.find_elements_by_tag_name('li')
            for elemento in listas_datos:
                elemento_strong = elemento.find_element_by_tag_name('strong').text
                elemento_span = elemento.find_element_by_tag_name('span').text
                self.dict_datos[elemento_strong] = [elemento_span]
        except Exception as e:
            print(e)
        
        
    def price(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'specs-list')))
            elemento_precio = self.driver.find_element_by_class_name('price-tag.price-tag-motors')
            self.precio = elemento_precio.find_element_by_class_name('price-tag-fraction').text
            self.dict_datos['precio'] = [self.precio]
        except Exception as e:
            print(e)
            self.dict_datos['precio'] = ['NA']




# se corre la clase que obtiene informacion para cada articulo

def corre_clase_articulo():
    # corre el primer articulo
    class_article = articulo_tu_carro_co()
    class_article.inicia_articulo(class_tu_carro.list_urls[0])
    class_article.obtiene_imagenes()
    class_article.datos_articulo()
    class_article.price()
    contador = 0
    df_articulo = pd.DataFrame(class_article.dict_datos)
    df_articulo.to_csv('/path/para/guardar/articulo/articulo_' + str(contador) + '.csv')
    # corre el resto de los articulos de la lista
    for url in class_tu_carro.list_urls:
        try:
            print(contador)
            contador = contador + 1
            class_article.inicia_articulo(url)
            class_article.obtiene_imagenes()
            class_article.datos_articulo()
            class_article.price()
            df_articulo = pd.DataFrame(class_article.dict_datos)
            df_articulo.to_csv('/path/para/guardar/articulo/articulo_' + str(contador) + '.csv')
            #df_base = df_base.append(df_articulo)
        except Exception as e:
            print(e)
            continue
    class_article.driver.quit()



df_articulos = corre_clase_articulo()


'''
Uniendo los csvs
Finalmente hay que unir todos los csv en un unico csv 
'''


path_csvs = "/path/para/guardar/articulo/"
files = listdir(path_csvs)    
files = [x for x in files if x.endswith('.csv')]
df_total = pd.DataFrame()
for i,file in enumerate(files):
    csv = pd.read_csv(path_csvs + files[i])
    df_total = df_total.append(csv)



df_total.to_csv("/path/para/guardar/data/completa/data_tu_carro_co_complete.csv", index = False)

        

