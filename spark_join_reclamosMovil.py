#!/usr/bin/env python
# coding: utf-8

#####################################################################
# TELEFONICA DEL PERU - Reporte Reclamos ALDM
# SCRIPT ID       : script_Reclamos_ALDM.py
# DESCRIPCION     : Se recibe un archivo plano de reclamos y se realiza un cruce con la informacion de los ultimos 3 meses de tasados movil Post Pago
# NOTAS           : 
# PARAMETROS      : HDFS_FILE_RECLAMOS = sys.argv[1], NUM_MONTH = sys.argv[2]
# AUTOR           : TELEFÓNICA DEL PERU
# BITACORA DE CAMBIOS :
# VER.  FECHA       HECHO POR            COMENTARIOS
# --------------------------------------------------------------------------------------------------------------------
# 1.0   2021/06/01  Jose Mayuri        Version inicial
# --------------------------------------------------------------------------------------------------------------------
########################################################################

#import findspark
#findspark.init("/usr/hdp/current/spark2-client")
import sys
import os
import glob
import datetime
import logging
import subprocess
import re, csv
from io import StringIO
import os
import shlex
import uuid
import pyspark.sql.functions as f

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from pyspark.context import SparkContext
from pyspark.sql.context import SQLContext
from pyspark import SparkConf
from pyspark.sql import SparkSession, HiveContext
from myconfig_join_reclamos import *

def verifyFileHdfs(path_file):
    try:
       args = "hdfs dfs -test -e "+path_file
       val = subprocess.check_call(args, shell=True)
    except subprocess.CalledProcessError as e:
       val = 1
    return val

def hdfs_move(fOrigPath,fTargPath):
    input=fOrigPath
    target=fTargPath
    cmd = '-mv'
    proc = subprocess.Popen(['hadoop', 'fs', cmd, fOrigPath,fTargPath],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=False)
    output, error = proc.communicate()
    if proc.returncode != 0:
        print_with_logging('No se logró mover el archivo del directorio HDFS '+fOrigPath+' a '+fTargPath, 'error')
        print_with_logging(proc.returncode + ' '+ output+' ' + error, 'error')
    print_with_logging('Se movió el archivo del directorio HDFS: '+input+' a HDFS: '+target, 'info')
    return output
    
def hdfs_create_folder(hdfs_Path):
    input = hdfs_Path
    cmd = '-mkdir'
    proc = subprocess.Popen(['hdfs', 'dfs', cmd, '-p', hdfs_Path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=False)
    output, error = proc.communicate()
    if proc.returncode != 0:
        print_with_logging('No se logra crear la carpeta en HDFS ' + hdfs_Path, 'error')
        print_with_logging(proc.returncode + ' ' + output + ' ' + error, 'error')
    print_with_logging('Se crea la carpeta en HDFS: ' + input, 'info')
    return output
    
def hdfs_remove(fHDFSPath):
    path_file=fHDFSPath
    cmd = '-rm'
    proc = subprocess.Popen(['hadoop', 'fs', cmd, path_file],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=False)
    output, error = proc.communicate()
    if proc.returncode != 0:
        print_with_logging('No se logró remover el archivo del directorio HDFS '+path_file, 'error')
        print_with_logging(proc.returncode + ' '+ output+' ' + error, 'error')
    print_with_logging('Se removió el archivo del directorio HDFS: '+path_file, 'info')
    return output

def print_with_logging(str, level):
    print( str )
    if level =='error':
        logging.error( str )
    elif level == 'warning':
        logging.warning( str )
    elif level == 'info':
        logging.info( str )
    else:
        logging.info( str )
        
def repeat_character(character, length):
    return character * length

HDFS_FILE_RECLAMOS = sys.argv[1]
HDFS_FILE_CATALOGO = sys.argv[2]
NUM_MONTH = sys.argv[3]

#Crea archivos log
current_date=datetime.datetime.now().strftime("%Y%m%d")
path_log_current_date=FS_PATH_LOG_MOVIL+'/'+current_date+'/'
if not os.path.exists(path_log_current_date):
   os.makedirs(path_log_current_date, 0o775)
   print_with_logging("Se creó el directorio: " + path_log_current_date, 'info')
process_time=datetime.datetime.now().strftime("%Y%m%d%H%M")
file_log=path_log_current_date+'reclamos_tasado_movil_'+process_time+'.log'

#Se crea log de ejecución
# Resetear los handlers del logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename=file_log, filemode="w", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print_with_logging( repeat_character('-', 100), 'info' )
#Se abre la sesión de Spark
print_with_logging('Se abre sesion Spark', 'info')
conf = SparkConf()
#conf.setMaster('yarn') #yarn in prod
conf.setMaster("local[2]")
conf.set("spark.shuffle.service.enabled", "true")
conf.set("spark.dynamicAllocation.enabled", "true")
conf.set("spark.driver.cores", "12")
conf.set("spark.driver.memory", "12G")
conf.set("spark.executor.memory", "12G")
conf.set("spark.executor.cores", "6")
conf.set("spark.executor.instances", "4")
conf.set("spark.sql.shuffle.partitions", "1000")
conf.set("spark.rdd.compress", "true")
conf.set("spark.sql.debug.maxToStringFields", 1000)
conf.set("spark.local.dir", '/srv/BigData/spark/tmp')

sc = SparkContext(conf=conf)
sqlContext = HiveContext(sc)
appName='mediosProbatoriosMovil'

DAY_NOW = datetime.datetime.now()
DAY_INI = DAY_NOW - relativedelta(months=int(NUM_MONTH))
DIFFERENCE_DAYS = abs((DAY_NOW - DAY_INI).days) + 1

try:
    spark = SparkSession.builder.appName(appName).enableHiveSupport().getOrCreate()
    spark.conf.set("spark.sql.debug.maxToStringFields", 1000)
    print_with_logging('Se creó la Sesión Spark con AppName: '+appName, 'info')
except Exception as e:
    print_with_logging('No se logró crear Sesión Spark con AppName: '+appName, 'error')
    logging.error('Detalle: ',exc_info=e)
    sys.exit(1)
    
# Se carga el archivo de reclamos
try:
    FS_PATH_FINAL = HDFS_PATH_INPUT_RECLAMOS_MOVIL+"/"+HDFS_FILE_RECLAMOS
    df_Reclamos = spark.read.format("csv").\
                 option("header", "true").\
                 option("inferschema","true").\
                 option("delimiter", "|").\
                 load(FS_PATH_FINAL)
    print_with_logging("Se carga la informacion de reclamos del archivo "+FS_PATH_FINAL, 'info')
except Exception as e:
    print_with_logging('No se logra cargar el archivo: ' + FS_PATH_FINAL, 'error')
    print_with_logging('Detalle: ' + str(e), 'error')
    logging.error('Detalle: ', exc_info=e)
    spark.stop()
    sys.exit(1)

# Se carga el archivo de catalogos de operadoras
try:
    FS_PATH_FINAL = HDFS_PATH_CATALOGO_OPER+"/"+HDFS_FILE_CATALOGO
    df_catalogo_operadoras = spark.read.format("csv").\
                             option("header", "true").\
                             option("inferschema","true").\
                             option("delimiter", "|").\
                             load(FS_PATH_FINAL)
    print_with_logging("Se carga la informacion de catalogos de operadoras del archivo "+FS_PATH_FINAL, 'info')
except Exception as e:
    print_with_logging('No se logra cargar el archivo: ' + FS_PATH_FINAL, 'error')
    print_with_logging('Detalle: ' + str(e), 'error')
    logging.error('Detalle: ', exc_info=e)
    spark.stop()
    sys.exit(1)

# Se carga la informacion de tasado movil post-pago
try:
    #Calculo de rango de fechas
    df_tasado_post_movil = sqlContext.createDataFrame([], COLUMNS_TASADO_POST_MOVIL)
    for DAY in (DAY_INI + timedelta(days=n) for n in range(DIFFERENCE_DAYS)):
        FS_PATH_DAY = HDFS_PATH_INPUT_TASADO_POST_MOVIL+'/'+DAY.strftime("%Y%m%d")+'/*/*.DAT'
        try:
            #df_tasado_post_movil = spark.read.format("orc").\
            #                       option("header","true").\
            #                       option("inferschema","true").\
            #                       load(FS_PATH_DAYS_POST_PAGO)
            df_tasado_post_movil = df_tasado_post_movil.unionAll(
                                                                 spark.read.format("csv").\
                                                                 option("header","false").\
                                                                 option("delimiter","|").\
                                                                 schema(COLUMNS_TASADO_POST_MOVIL).\
                                                                 load(FS_PATH_DAY)
                                                                )
        except Exception as e:
            pass
    print_with_logging("Se carga la informacion de tasado movil post pago desde el dia "+DAY_INI.strftime("%d-%m-%Y")+ " hasta el "+ DAY_NOW.strftime("%d-%m-%Y"), 'info')
except Exception as e:
    print_with_logging("No se logra cargar el dataframe con la informacion de tasado post-movil", 'error')
    print_with_logging('Detalle: ' + str(e), 'error')
    logging.error('Detalle: ', exc_info=e)
    spark.stop()
    sys.exit(1)
    
try:
    df_Filter_Tasado = df_tasado_post_movil.alias("TP").\
                     filter(
                            (f.trim(f.col("TP.CodTipServTraf")) == f.lit("S")) | 
                            (f.trim(f.col("TP.CodTipServTraf")) == f.lit("V"))
                           ).\
                     select(f.trim(f.col("TP.FecIni")).alias("FECHA_INICIO_LLAMADA"), 
                            f.trim(f.col("TP.HoraIni")).alias("HORA_INICIO_LLAMADA"), 
                            f.trim(f.col("TP.CodSentTraf")).alias("TIPO_LLAMADA"),
                            f.trim(f.col("TP.DurReal")).alias("DURACION_LLAMADA"),
                            f.lit("TASADO").alias("TIPO_EVENTO"),
                            f.lit("TASADO").alias("SUBTIPO_EVENTO"),
                            f.trim(f.col("TP.NumOri")).alias("NUMERO_ORIGEN"),
                            f.trim(f.col("TP.NumDest")).alias("NUMERO_DESTINO"),
                            f.trim(f.col("TP.CodOper")).alias("CODE_OPER"),
                            f.trim(f.col("TP.CodEstValor")).alias("VALOR"),
                            f.trim(f.col("TP.CodTipServTraf")).alias("TIPO_TRAFICO")
                           )
                    
    print_with_logging("Se carga la informacion consolidada de tasado movil desde el dia "+DAY_INI.strftime("%d-%m-%Y")+ " hasta el "+ DAY_NOW.strftime("%d-%m-%Y"), 'info')
except Exception as e:
    print_with_logging("No se logra cargar el dataframe con la informacion consolidada de tasado", 'error')
    print_with_logging('Detalle: ' + str(e), 'error')
    logging.error('Detalle: ', exc_info=e)
    spark.stop()
    sys.exit(1)

try:
    df_Reclamos_Detalle = df_Reclamos.alias("R").join(
                                                       df_Filter_Tasado.alias("T"), 
                                                       (f.col("R.SUSCRIPCION") == f.col("T.NUMERO_ORIGEN")) | 
                                                       (f.col("R.SUSCRIPCION") == f.col("T.NUMERO_DESTINO"))
                                                     ).\
                                                 join(
                                                       df_catalogo_operadoras.alias("C"),
                                                       (f.col("T.CODE_OPER") == f.col("C.CODE_OPER")),
                                                       how="left"
                                                     ).\
                                               select( 
                                                       f.lit("NIFI").alias("TEMPLATEID"),
                                                       f.col("R.ID_CORRELATIVO_RECLAMO"),
                                                       f.col("R.CLIENTE"),
                                                       f.col("R.SUSCRIPCION"),
                                                       f.col("R.CICLO"),
                                                       f.col("R.CUENTA_FINANCIERA"),
                                                       f.col("T.FECHA_INICIO_LLAMADA"),
                                                       f.col("T.HORA_INICIO_LLAMADA"),
                                                       f.col("T.TIPO_LLAMADA"),
                                                       f.col("T.DURACION_LLAMADA"),
                                                       f.col("T.TIPO_EVENTO"),
                                                       f.col("T.SUBTIPO_EVENTO"),
                                                       f.col("T.NUMERO_DESTINO"),
                                                       f.when(f.col("C.CODE_OPER").isNull(), f.col("T.CODE_OPER")).\
                                                            otherwise(f.col("C.DESCRIPTION")).\
                                                            alias("DESCRIPCION_OPERADORA"),
                                                       f.col("T.VALOR"),
                                                       f.col("T.TIPO_TRAFICO"),
                                                       f.col("R.CODIGO_CLIENTE"),
                                                       f.col("R.ID_SUSCRIPCION"),
                                                       f.col("R.TIPO_DOCUMENTO_CLIENTE"),
                                                       f.col("R.NUMERO_DOCUMENTO_CLIENTE"),
                                                       f.col("R.SEGMENTO")
                                                     )       
    print_with_logging("Se obtuvo el detalle de los reclamos con respecto a los ultimos "+NUM_MONTH+" meses", 'info')
except Exception as e:
    print_with_logging("No se logra cargar el dataframe con el detalle de reclamos", 'error')
    print_with_logging('Detalle: ' + str(e), 'error')
    logging.error('Detalle: ', exc_info=e)
    spark.stop()
    sys.exit(1)
    
# Se exporta el archivo csv a ruta HDFS 
try:
    df_Reclamos_Detalle.repartition(1).\
                        write.format("com.databricks.spark.csv").\
                        mode("overwrite").\
                        option("header","false").\
                        option("delimiter", '|').\
                        option("quoteMode", "false").\
                        save(HDFS_PATH_INPUT_RECLAMOS_XML_MOVIL)
    print_with_logging("Se escribieron los datos correctamente en el directorio HDFS: " + HDFS_PATH_INPUT_RECLAMOS_XML_MOVIL, 'info')
    hdfs_create_folder(HDFS_PATH_PROC_RECLAMOS_MOVIL+"/"+current_date)
    val = verifyFileHdfs(HDFS_PATH_PROC_RECLAMOS_MOVIL+"/"+current_date+"/"+HDFS_FILE_RECLAMOS)
    if not val:
       hdfs_remove(HDFS_PATH_PROC_RECLAMOS_MOVIL+"/"+current_date+"/"+HDFS_FILE_RECLAMOS)
    hdfs_move(HDFS_PATH_INPUT_RECLAMOS_MOVIL+"/"+HDFS_FILE_RECLAMOS, HDFS_PATH_PROC_RECLAMOS_MOVIL+"/"+current_date)
except Exception as e:
    print_with_logging('No se logra escribir los datos en el directorio HDFS: ' + HDFS_PATH_INPUT_RECLAMOS_XML_MOVIL, 'error')
    print_with_logging('Detalle: ' + str(e), 'error')
    logging.error('Detalle: ', exc_info=e)
    spark.stop()
    sys.exit(1)

print_with_logging(repeat_character('-', 100), 'info')
print_with_logging('Proceso Finalizado.', 'info')
spark.stop()