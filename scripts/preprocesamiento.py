# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 23:13:16 2019

@author: Mercy Pinargote
"""

import os
import pandas as pd
import numpy as np
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals())

directory = os.path.join("C://","Tesis/Datos")
for root,dirs,files in os.walk(directory):
    for file in files:
       if file.endswith(".csv"):
           #importar archivos de calidad aire      
            file_path =os.path.join(directory,file)
            datos_aire_horarios= pd.read_csv(file_path , sep=";")
            header_list = list(datos_aire_horarios)
            columns_name = header_list[1:8]
            columns_name.append("Valido")
            columns_name.append("Hora1")
            columns_name.append("VALOR")
            columns_name.append("HORA")            
            columns_name.append("HSEN")   
            columns_name.append("HCOS")   
            
            datos_aire_horarios_pro= pd.DataFrame(columns=columns_name)
            
            for i in range(1,24):    
                lista = header_list[1:8]
                lista.append( "V" + ("0"+str(i))[-2:])
                hora ="H" + ("0"+str(i))[-2:]
                datos_aire_horarios1 = pd.melt(datos_aire_horarios, id_vars=lista, value_vars=hora )
                #Transformar hora para evaluar eventos ciclicos
                datos_aire_horarios1["HORA"]=i                
                datos_aire_horarios1["HSEN"]=np.sin(2*np.pi/24*i)
                datos_aire_horarios1["HCOS"]=np.cos(2*np.pi/24*i)
                datos_aire_horarios1.columns = columns_name                    
                datos_aire_horarios_pro = datos_aire_horarios_pro.append(datos_aire_horarios1)
            #eliminar todos los datos que nos son validos
            datos_aire_horarios_pro = datos_aire_horarios_pro[(datos_aire_horarios_pro.Valido =='V')]
#crear columna fecha
datos_aire_horarios_pro ["FECHA"] = pd.to_datetime(datos_aire_horarios_pro["ANO"].map(str) +"-"+datos_aire_horarios_pro["MES"].map(str)+"-"+ datos_aire_horarios_pro["DIA"].map(str))
datos_aire_horarios_pro= datos_aire_horarios_pro[["FECHA", 'ESTACION', 'MAGNITUD', 'HSEN', 'HCOS', 'VALOR'] ]      
#cargar lista de contaminate
contaminante_clave= pd.read_csv('contaminante_clave.csv', sep=",")

datos_aire_horarios_pro = pd.merge(datos_aire_horarios_pro, contaminante_clave , copy=False)
#crear table para utilizar en las redes neuronales
datos_aire_horarios_pro = pd.pivot_table(datos_aire_horarios_pro, columns='CONTAMINANTE', values=['VALOR'], index=['FECHA','HSEN','HCOS'], aggfunc=np.mean).reset_index()
datos_aire_horarios_pro
#convertir la tabla en una archivo plano para usar en los experimientos
flattened = pd.DataFrame(datos_aire_horarios_pro.to_records(index=False))
flattened.columns = ['FECHA', 'HSEN','HCOS',  'BEN',  'CH4',  'CO',  'EBE','NMHC',  'NO',  'NO2',  'NOx',  'O3', 'PM10',  'PM25',  'SO2',  'TCH',  'TOL'] 
flattened.to_csv('datos_transformados.csv') 