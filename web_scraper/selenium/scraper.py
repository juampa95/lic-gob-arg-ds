# -*- coding: utf-8 -*-
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



# =============================================================================
# Datos iniciales
# =============================================================================

df =pd.read_csv('D:/gitProyects/licitacionesEstatales-ds/ReporteProcesos.csv')
df['Número de Proceso'][0]


# =============================================================================
# Scraper 
# =============================================================================

driver = webdriver.Chrome(ChromeDriverManager().install())

for i in range(4):
    indice = df['Número de Proceso'][i]  
    driver.get("https://comprar.gob.ar/BuscarAvanzado.aspx")
    time.sleep(1)
    buscador = driver.find_element(By.ID, "ctl00_CPH1_txtNumeroProceso")
    time.sleep(1)
    buscador.send_keys(indice)
    time.sleep(1)
    driver.find_element(By.ID,"ctl00_CPH1_btnListarPliegoNumero").click()
    time.sleep(1)
    detalle = driver.find_element(By.XPATH,"//tbody/tr/td/a").click()
    time.sleep(1)  
      
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
    
    
    s_info = pd.Series(info['Información básica del proceso'])
    # CON ESTAS LINEAS OBTENEMOS LOS DATOS DEL CRONOGRAMA 
    
    crono = {}
    cronograma = {}
    cronograma_titulos = driver.find_elements(By.XPATH,'//div[div[h4[text()="Cronograma"]]]//label')
    cronograma_fechas = driver.find_elements(By.XPATH,'//div[div[h4[text()="Cronograma"]]]//p/span')
    try:
        for i in range(len(cronograma_titulos)):
            crono[cronograma_titulos[i].text]=cronograma_fechas[i].text
            cronograma['cronograma'] = crono
    except:
        pass
    s_crono = pd.Series(crono)
    # CON ESTAS LINEAS OBTENEMOS TODOS LOS DATOS DE LOS ELEMENTOS QUE SON TABLAS 
    
    nomb_col = driver.find_elements(By.XPATH,'//div[h4[text()="Documento contractual por proveedor"] and //table[thead and tbody]]//th')
    cant_filas = driver.find_elements(By.XPATH,'//div[h4[text()="Documento contractual por proveedor"] and //table[thead and tbody]]//tbody//tr')
    valores_tablas = driver.find_elements(By.XPATH,'//div[h4[text()="Documento contractual por proveedor"] and //table[thead and tbody]]//td')
    
    # VERSION MAS ACTUAL PARA QUE TODO ENTRE EN UNA SERIE DE PANDAS 
    h4 = driver.find_elements(By.XPATH,'//div/h4')
    dic_tablas = {}
    try:
        for h in h4:
            nomb_col = driver.find_elements(By.XPATH,f'//div[h4[text()="{h.text}"] and //table[thead and tbody]]//th')
            if len(nomb_col) != 0:
                cant_filas = driver.find_elements(By.XPATH,f'//div[h4[text()="{h.text}"] and //table[thead and tbody]]//tbody//tr')
                filas_datos = {}
                if len(cant_filas) != 1:
                    fila_datos = {}
                    for i in range(1,len(cant_filas)+1):
                        
                        valores_tablas = driver.find_elements(By.XPATH,f'//div[h4[text()="{h.text}"] and //table[thead and tbody]]//tbody//tr[{i}]/td')
                        for p in range(len(nomb_col)):
                            fila_datos[nomb_col[p].text + str(i)] = valores_tablas[p].text
                            fila_datos.update(fila_datos)
                        filas_datos = fila_datos
                else:
                    fila_datos = {}
                    valores_tablas = driver.find_elements(By.XPATH,f'//div[h4[text()="{h.text}"] and //table[thead and tbody]]//tbody//tr/td')
                    for j in range(len(nomb_col)):
                        fila_datos[nomb_col[j].text] = valores_tablas[j].text
                    
                    filas_datos = fila_datos
                dic_tablas[h.text] = filas_datos
    except:
        pass
    
    s_tablas = pd.Series()
    
    for i in dic_tablas:
        s_tablas = pd.concat([s_tablas,pd.Series(dic_tablas[i])])
                              
    # AHORA VAMOS A TENER QUE HACER CLICK EN EL CUADRO COMPARATIVO PARA VER LOS PRECIOS QUE OFERTARON LOS COMPETIDORES
    
    driver.find_element(By.XPATH,'//div[a[@class="btn btn-link"]]/a').click()
    emp = driver.find_elements(By.XPATH,'//div[span[h4[text()="Mostrar ofertas"]]]//div[@class="col-md-9"]/span')
    ofertas = driver.find_elements(By.XPATH,'//div[span[h4[text()="Mostrar ofertas"]]]//div[@class="col-md-3"]/span')
    
    empresas = []
    ofer = {}    
    try:
        
        for i in emp:
            if i.text != "":
                empresas.append(i.text)
                
    
        for i in range(len(ofertas)):
            ofer["empresa_"+str(i)]=empresas[i]
            ofer["oferta_"+str(i)]=ofertas[i].text
    except:
        pass
    s_ofer = pd.Series(ofer)
    
    s_total = pd.Series()
    s_total = s_total.append([s_info,s_crono,s_tablas,s_ofer])
    s_total['Número de Proceso'] = s_total['Nº de proceso'] # esto es necesario hacerlo para poder hacer un merge con el df original 
    
    s_total

    df2 = pd.merge(df, s_total.to_frame().T, on = 'Número de Proceso', how = 'outer')

df2.iloc[0,40:60]
