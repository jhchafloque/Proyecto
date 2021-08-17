#!/usr/bin/env python
# coding: utf-8

# # Ejemplo

# In[14]:


#Se importan las librerias
import sys
import glob
import os
import datetime
import logging
import subprocess
#from importlib import reload
import re, csv
from io import StringIO
import shlex
import uuid
import pandas as pd
import shutil


# In[36]:


#Declarando las funciones
def func(x):
    if x == '+10%':
        return 0.1
    elif x == '+6%':
        return 0.06
    elif x == '-10%':
        return -0.1
    elif x == '-6%':
        return -0.06
    return 0


# In[17]:


#Declarando las funciones
def print_with_logging(str, level):
    print( str )
    if level == 'error':
        logging.error(str)
    elif level == 'warning':
        logging.warning(str)
    elif level == 'info':
        logging.info(str)
    else:
        logging.info(str)


# In[8]:


#Declarando las rutas
# path_data = argv[1]
path_data = r"C:/Users/jhchafloque/Documents/Capacitacion Python/Data"
path_bin = r"C:/Users/jhchafloque/Documents/Capacitacion Python/Bin"
file = 'BD_CONSUMO_FUEL.csv'

process_name = 'prueba'


# In[9]:


path_input = path_data + '/input/'
path_processed = path_data + '/processed/'
path_processing = path_data + '/processing/'
path_invalid = path_data + '/invalid/'
path_results = path_data + '/results/'


# In[10]:


load_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")


# In[11]:


path_log = path_bin + '/log/'
file_log = process_name + '_' + load_date + '.log'
path_file_log = path_log + file_log

print(path_log)
print(file_log)
print(path_file_log)


# In[15]:


if not os.path.exists(path_log):
    os.makedirs(path_log, 0o775) #Crea la carpeta y asigna los permisos
    print_with_logging("Se creo el directorio: "+ path_log , 'info')


# In[16]:


#Se crea el log de ejecucion
#Resetear los handlers del logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename=path_file_log, filemode="w", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# In[19]:


print_with_logging('Se creo el log del proceso :'+process_name,'info')
print_with_logging('path_bin :'+path_bin,'info')
print_with_logging('path_data :'+path_data,'info')
print_with_logging('path_input :'+path_input,'info')
print_with_logging('path_processed :'+path_processed,'info')
print_with_logging('path_log :'+path_file_log,'info')


# In[20]:


file_to_read = path_input + file
print(file_to_read)


# In[22]:


try:
    data = pd.read_csv(file_to_read)
    print_with_logging('\nSe logro abrir el archivo' + file_to_read , 'info')
    #data.head()
    print_with_logging(data.head(),'info')
except Exception as e:
    print_with_logging('Error al intentar leer el archivo','error')
    print_with_logging('Moviendo el archivo a invalid','error')
    shutil.move(file_to_read, path_invalid + file)
    #Para que el programa acabe
    #sys.exit(1)
    


# In[23]:


try:
    with open(file_to_read, "r") as fichero:
        for linea in fichero:
            print (linea)
except:
    print('No se pudo leer el archivo')
    


# In[24]:


print_with_logging('Moviendo el archivo a la ruta de processing ' + path_processing + file, 'info')
shutil.move(file_to_read, path_processing + file)


# In[30]:


data.head(3)


# In[26]:


#Viendo los tipos de datos que tiene el archivo
data.dtypes


# In[34]:


data.groupby('PENDIENTE_TOPO')['PENDIENTE_TOPO'].count()


# In[37]:


data['PENDIENTE_TOPO'].apply(func)


# In[38]:


data.head()


# In[39]:


data['PENDIENTE_TOPO_2'] = data['PENDIENTE_TOPO'].apply(func)
data.head()


# In[40]:


data.describe()


# In[ ]:


col = ['PENDIENTE_TOPO_2']


# In[41]:


data_final = data['PENDIENTE_TOPO_2']


# In[42]:


data_final.head()


# In[43]:


file_out= 'consumo_fuel_out'
file_results = path_results + file_out + '_' + load_date + '.csv'
print(file_results)


# In[45]:


data_final.to_csv(file_results,index=False,sep='|',header=True)


# In[46]:


print_with_logging('Moviendo el archivo de la ruta '+ path_processing + file + ' hacia la ruta ' + path_processed + file,'info')
#print(file_to_read)
shutil.move(path_processing + file, path_processed + file)

