# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 19:35:22 2023

@author: jpman
"""
"""
Created on Sat Mar  4 00:12:41 2023
@author: jpman
"""
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import csv
from io import StringIO
from datetime import datetime
from datetime import timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://comprar.gob.ar/BuscarAvanzado.aspx")
time.sleep(1)
buscador = driver.find_element(By.ID, "ctl00_CPH1_txtNumeroProceso")
time.sleep(1)
buscador.send_keys('101-0001-CDI20')
time.sleep(1)
driver.find_element(By.ID,"ctl00_CPH1_btnListarPliegoNumero").click()
time.sleep(1)
detalle = driver.find_element(By.XPATH,"//tbody/tr/td/a").click()
time.sleep(1)
titulos = driver.find_elements(By.TAG_NAME,'h4')

# for i in titulos:
#     print(i.text)

prubea = driver.find_elements(By.CLASS_NAME,'row')

for i in prubea:
    print(i.text)




#$x('//div[@class = "col-md-4"]/label/text()').map(elm => elm.wholeText)
# prueba4 = driver.find_elements(By.XPATH,'//div[@class = "col-md-4"]/p//span') 
#$x('//div[@class = "col-md-4"]/p/span/text()').map(elm => elm.wholeText)

# Con esta sentencia obtenemos todo lo que esta dentro de "INFORMACION BASICA DEL PROCESO"

titulos = driver.find_elements(By.XPATH,'//div[@class="col-md-4"]//label')

# una vez que tenemos todos los titulos, vamos a buscar los elementos /p/span 
# que contiene cada titulo. Este elemento es el texto debajo del titulo. 
info = {}
datos = {}
for i in range(len(titulos)):

    xpath = f'//div[label[contains(text(),"{titulos[i].text}")]]/p/span'
    texto = driver.find_elements(By.XPATH,xpath)
    pal = []
    for t in texto:
        if len(texto) == 1:
            datos[titulos[i].text] = t.text
        else:
            pal.append(t.text)  
            datos[titulos[i].text] = pal
    info['Información básica del proceso'] = datos

info

# CON ESTAS LINEAS OBTENEMOS LOS DATOS DEL CRONOGRAMA 

crono = {}
cronograma = {}
cronograma_titulos = driver.find_elements(By.XPATH,'//div[div[h4[text()="Cronograma"]]]//label')
cronograma_fechas = driver.find_elements(By.XPATH,'//div[div[h4[text()="Cronograma"]]]//p/span')

for i in range(len(cronograma_titulos)):
    crono[cronograma_titulos[i].text]=cronograma_fechas[i].text
    cronograma['cronograma'] = crono

cronograma


# CON ESTAS LINEAS OBTENEMOS TODOS LOS DATOS DE LOS ELEMENTOS QUE SON TABLAS 

nomb_col = driver.find_elements(By.XPATH,'//div[h4[text()="Documento contractual por proveedor"] and //table[thead and tbody]]//th')
cant_filas = driver.find_elements(By.XPATH,'//div[h4[text()="Documento contractual por proveedor"] and //table[thead and tbody]]//tbody//tr')
valores_tablas = driver.find_elements(By.XPATH,'//div[h4[text()="Documento contractual por proveedor"] and //table[thead and tbody]]//td')


h4 = driver.find_elements(By.XPATH,'//div/h4')
dic_tablas = {}
for h in h4:
    nomb_col = driver.find_elements(By.XPATH,f'//div[h4[text()="{h.text}"] and //table[thead and tbody]]//th')
    if len(nomb_col) != 0:
        cant_filas = driver.find_elements(By.XPATH,f'//div[h4[text()="{h.text}"] and //table[thead and tbody]]//tbody//tr')
        filas_datos = {}
        if len(cant_filas) != 1:
            for i in range(1,len(cant_filas)+1):
                fila_datos = {}
                valores_tablas = driver.find_elements(By.XPATH,f'//div[h4[text()="{h.text}"] and //table[thead and tbody]]//tbody//tr[{i}]/td')
                for p in range(len(nomb_col)):
                    fila_datos[nomb_col[p].text] = valores_tablas[p].text
                filas_datos[str(i-1)] = fila_datos
        else:
            fila_datos = {}
            valores_tablas = driver.find_elements(By.XPATH,f'//div[h4[text()="{h.text}"] and //table[thead and tbody]]//tbody//tr/td')
            for j in range(len(nomb_col)):
                fila_datos[nomb_col[j].text] = valores_tablas[j].text
            
            filas_datos = fila_datos
        dic_tablas[h.text] = filas_datos
        
dic_tablas


# AHORA VAMOS A TENER QUE HACER CLICK EN EL CUADRO COMPARATIVO PARA VER LOS PRECIOS QUE OFERTARON LOS COMPETIDORES

driver.find_element(By.XPATH,'//div[a[@class="btn btn-link"]]').click()
emp = driver.find_elements(By.XPATH,'//div[span[h4[text()="Mostrar ofertas"]]]//div[@class="col-md-9"]/span')
ofertas = driver.find_elements(By.XPATH,'//div[span[h4[text()="Mostrar ofertas"]]]//div[@class="col-md-3"]/span')

empresas = []
for i in emp:
    if i.text != "":
        empresas.append(i.text)
        
ofer = {}
total_ofertas = {}
for i in range(len(ofertas)):
    ofer[empresas[i]]=ofertas[i].text
total_ofertas['Ofertas'] = ofer
        
total_ofertas

total_informacion = {}

total_informacion.update(info)
total_informacion.update(cronograma)
total_informacion.update(dic_tablas)
total_informacion.update(total_ofertas)

total_informacion

with open('prueba.json','w') as archivo:
    json.dump(total_informacion, archivo)
    
df = pd.read_json('D:/gitProyects/licitacionesEstatales-ds/web_scraper/prueba.json')
df.columns
df['Ofertas']

df_info = pd.DataFrame(info)
df_info
df_cronograma=pd.DataFrame(cronograma)
df_cronograma

dic_tablas.keys()
pd.DataFrame.from_dict(dic_tablas['Solicitudes de contratación asignadas al proceso'],orient='index')
pd.DataFrame.from_dict(dic_tablas['Detalle de productos o servicios'],orient='index')
pd.DataFrame.from_dict(dic_tablas['Pliego de bases y condiciones generales'],orient='index')
pd.DataFrame.from_dict(dic_tablas['Penalidades'],orient='index')
pd.DataFrame.from_dict(dic_tablas['Selección de proveedores'],orient='index')
pd.DataFrame.from_dict(dic_tablas['Actas de apertura'],orient='index')
pd.DataFrame.from_dict(dic_tablas['Documento contractual por proveedor'],orient='index')

df_total_ofertas = pd.DataFrame(total_ofertas)
df_total_ofertas
