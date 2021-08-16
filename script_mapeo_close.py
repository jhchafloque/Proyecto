#!/usr/bin/env python
# coding: utf-8
# ------------------------------------------------------------
# TELEFONICA DEL PERU
# Proceso         : Actualizacion Cancelacion CASO II
# Descripción     : Permite realizar el mapeo de XML
# Argumentos      : p_file = sys.argv[1] - Ingresa el nombre del archivo plano
# Autor           : INDRA
# Bitácora de cambios:
# ------------------------------------------------------------
# Version   Fecha       Autor                Comentario
# 1.0       20210708    Jhon Chafloque       Versión inicial
# ------------------------------------------------------------
import sys
import datetime
import os
import logging
import xml.etree.cElementTree as ET
from myconfig_close import *

def print_with_logging(str, level):
    if level == 'error':
        print(str)
        logging.error(str)
    elif level == 'warning':
        logging.warning(str)
    elif level == 'info':
        logging.info(str)
    else:
        logging.info(str)

#VARIABLES
p_file = sys.argv[1]

current_date = datetime.datetime.now().strftime("%Y%m%d")
name_process = V_PROCESS_MAPEO
path_log = V_PATH_LOG
filename = V_PATH_INPUT + "/" + p_file
path_mapping = V_PATH_MAPPING


#GENERAR ARCHIVO DE MAPEO
path_filename_xml_2 = path_mapping + '/' + p_file


#CREANDO DIRECTORIO LOG PARA LA FECHA ACTUAL
path_log_current_date = path_log + '/' + 'close_mapping' + '/' + current_date + '/'

if not os.path.exists(path_log_current_date):
    os.makedirs(path_log_current_date, 0o777)  # CREA LA CARPETA Y ASIGNA LOS PERMISOS
    print_with_logging("Se creo el directorio: " + path_log_current_date, 'info')

process_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
file_log = path_log_current_date + name_process + '_' + process_time + '.log'

#SE CREA LOG DE EJECUCION
#RESETEAR LOS HANDLERS DEL LOGGING
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename=file_log, filemode="w", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print_with_logging('Inicio de Ejecucion del proceso', 'info')
print_with_logging('Nombre del proceso: ' + name_process, 'info')
print_with_logging('Ruta Log: ' + path_log_current_date, 'info')
print_with_logging('Nombre del Archivo: ' + filename, 'info')

#INICIO DE PROCESO DE MAPEO
print_with_logging('Inicio de proceso de mapping de XML', 'info')

try:

    #LEER ARCHIVO QUE CONTIENE EL XML
    tree = ET.parse(filename)
    root = tree.getroot()
      
    #CONFIGURACIÓN DE NAMESPACES
    ns = {'soapenv':'http://schemas.xmlsoap.org/soap/envelope/',
          'typ':'http://telefonica.pe/RevenueAssuranceManagement/TroubleReportsAndAlarms/TroubleTicketing/V1/types',
          'v1':'http://telefonica.pe/TefRequestHeader/V1'}

    #MAPEO DE LOS TAGs
    envelope = ET.Element('soapenv:Envelope', attrib={'xmlns:soapenv':'http://schemas.xmlsoap.org/soap/envelope/'
                                                     ,'xmlns:typ':'http://telefonica.pe/RevenueAssuranceManagement/TroubleReportsAndAlarms/TroubleTicketing/V1/types'
                                                     ,'xmlns:v1':'http://telefonica.pe/TefRequestHeader/V1'})

    header1 = ET.SubElement(envelope, 'soapenv:Header')
    body = ET.SubElement(envelope, 'soapenv:Body')

    #HEADER
    #headerIn = ET.SubElement(header1, 'head:HeaderIn')
    #country = ET.SubElement(headerIn, 'head:country')
    #lang = ET.SubElement(headerIn, 'head:lang')
    #entity = ET.SubElement(headerIn, 'head:entity')
    #system = ET.SubElement(headerIn, 'head:system')
    #subSystem = ET.SubElement(headerIn, 'head:subsystem')
    #originator = ET.SubElement(headerIn, 'head:originator')
    #userId = ET.SubElement(headerIn, 'head:userId')
    #operation = ET.SubElement(headerIn, 'head:operation')
    #pid = ET.SubElement(headerIn, 'head:pid')
    #execId = ET.SubElement(headerIn, 'head:execId')
    #msgId = ET.SubElement(headerIn, 'head:msgId')
    #timeStamp = ET.SubElement(headerIn, 'head:timestamp')
    #msgType = ET.SubElement(headerIn, 'head:msgType')

    #BODY
    canCustomerProblemRequest = ET.SubElement(body, 'v1:CloseCustomerProblemRequest')
    canTefHeaderReq = ET.SubElement(canCustomerProblemRequest, 'v1:TefHeaderReq')
    userLogin = ET.SubElement(canTefHeaderReq, 'v1:userLogin')
    sessionCode = ET.SubElement(canTefHeaderReq, 'v1:sessionCode')
    application = ET.SubElement(canTefHeaderReq, 'v1:application')
    idMessage = ET.SubElement(canTefHeaderReq, 'v1:idMessage')
    transactionTimestamp = ET.SubElement(canTefHeaderReq, 'v1:transactionTimestamp')
    
    canCustomerProblemRequest_data = ET.SubElement(canCustomerProblemRequest, 'typ:CloseCustomerProblemRequest_data')
    canproblemReference = ET.SubElement(canCustomerProblemRequest_data, 'typ:problemReference')
    id = ET.SubElement(canproblemReference, 'typ:id')
    referenceNumber = ET.SubElement(canproblemReference, 'typ:referenceNumber')
    
    closeSummariesList = ET.SubElement(canCustomerProblemRequest_data, 'typ:closeSummariesList')
    problemSummary = ET.SubElement(closeSummariesList, 'typ:problemSummary')
    problemResolution = ET.SubElement(problemSummary, 'typ:problemResolution')
    code_s = ET.SubElement(problemResolution, 'typ:code')
    value_s = ET.SubElement(problemResolution, 'typ:value')
    
    canproblemStatus = ET.SubElement(canCustomerProblemRequest_data, 'typ:problemStatus')
    code = ET.SubElement(canproblemStatus, 'typ:code')
    value = ET.SubElement(canproblemStatus, 'typ:value')

    #OBTENER LOS DATOS HEADER DEL XML
    #for item_header in root.findall('./soapenv:Header', ns):
    #  #print(2)
    #  for item_headerIn in item_header.findall('./head:HeaderIn', ns):
    #    #print(3)
    #    in_country = item_headerIn.find('head:country',ns).text
    #    in_lang = item_headerIn.find('head:lang',ns).text
    #    in_entity = item_headerIn.find('head:entity',ns).text
    #    in_system = item_headerIn.find('head:system',ns).text
    #    in_subSystem = item_headerIn.find('head:subsystem',ns).text
    #    in_originator = item_headerIn.find('head:originator',ns).text
    #    in_userId = item_headerIn.find('head:userId',ns).text
    #    in_operation = item_headerIn.find('head:operation',ns).text
    #    ##in_pid = item_headerIn.find('head:pid',ns).text  EJEMPLO NO TRAE
    #    in_execId = item_headerIn.find('head:execId',ns).text
    #    ##in_msgId = item_headerIn.find('head:msgId',ns).text
    #    in_timeStamp = item_headerIn.find('head:timestamp',ns).text
    #    ##in_msgType = item_headerIn.find('head:msgType',ns).text
    #    country.text = in_country
    #    lang.text = in_lang
    #    entity.text = in_entity
    #    system.text = in_system
    #    subSystem.text = in_subSystem
    #    originator.text = in_originator
    #    userId.text = in_userId
    #    operation.text = in_operation
    #    ##pid.text = in_pid
    #    execId.text = in_execId
    #    ##msgId.text = in_msgId
    #    timeStamp.text = in_timeStamp
    #    ##msgType.text = in_msgType
    #
    #OBTENER LOS DATOS BODY DEL XML
    for item_body in root.findall('./soapenv:Body', ns):
      #print(4)
      for item_mttr in item_body.findall('./typ:CloseCustomerProblemRequest',ns):
          # detalle TefHeaderReq
          for item_TefHeaderReq in item_mttr.findall('./v1:TefHeaderReq', ns):
            #print(5)
            # values 
            in_userLogin = item_TefHeaderReq.find('v1:userLogin',ns).text
            userLogin.text = in_userLogin
            in_sessionCode = item_TefHeaderReq.find('v1:sessionCode',ns).text
            sessionCode.text = in_sessionCode
            in_application = item_TefHeaderReq.find('v1:application',ns).text
            application.text = in_application
            in_idMessage = item_TefHeaderReq.find('v1:idMessage',ns).text
            idMessage.text = in_idMessage
            in_transactionTimestamp = item_TefHeaderReq.find('v1:transactionTimestamp',ns).text
            transactionTimestamp.text = in_transactionTimestamp
        
          for item_CloseCustomerProblemRequest_data in item_mttr.findall('./typ:CloseCustomerProblemRequest_data',ns):
            # detalle problemReference
             for item_problemReference in item_CloseCustomerProblemRequest_data.findall('./typ:problemReference', ns):
               #print(5)
               # values 
               in_id = item_problemReference.find('typ:id',ns).text
               id.text = in_id
               in_referenceNumber = '' if (item_problemReference.find('typ:referenceNumber',ns) == None) else item_problemReference.find('typ:referenceNumber',ns).text
               referenceNumber.text = in_referenceNumber
           
            #closeSummariesList
             for item_closeSummariesList in item_CloseCustomerProblemRequest_data.findall('./typ:closeSummariesList', ns):
               print(7)
               # detalle problemSummary
               for item_problemSummary in item_closeSummariesList.findall('./typ:problemSummary', ns):
                 print(8)
                 for item_problemResolution in item_problemSummary.findall('./typ:problemResolution', ns):
                   # values 
                   in_code = item_problemResolution.find('typ:code',ns).text
                   code_s.text = in_code
                   in_value = '' if (item_problemResolution.find('typ:value',ns) == None) else item_problemResolution.find('typ:value',ns).text
                   value_s.text = in_value
           
            # detalle problemStatus
             for item_problemStatus in item_CloseCustomerProblemRequest_data.findall('./typ:problemStatus', ns):
               #print(5)
               # values 
               in_code = item_problemStatus.find('typ:code',ns).text
               code.text = in_code
               in_value = '' if (item_problemStatus.find('typ:value',ns) == None) else item_problemStatus.find('typ:value',ns).text
               value.text = in_value  
    
           
    #se va poner un prefijo con el filename_mapping
    tree = ET.ElementTree(envelope)
    tree.write(path_filename_xml_2)
       
    print_with_logging('Se culmina correctamente el proceso de mapping del XML: ' + path_filename_xml_2, 'info')
except Exception as e:
    print_with_logging('Ocurrio un error: Revisar el error en la carpeta ' + file_log, 'error')
    logging.error('Detalle: ', exc_info=e)
    print_with_logging('Fin de proceso de mapping del XML', 'info')
    sys.exit(1)

print_with_logging('Fin de proceso de mapping del XML', 'info')