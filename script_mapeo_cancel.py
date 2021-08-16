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
# 1.0       20210707    Addis Luna         Versión inicial
# ------------------------------------------------------------
import sys
import datetime
import os
import logging
import xml.etree.cElementTree as ET
from myconfig_cancel import *

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

# VARIABLES
p_file = sys.argv[1]

current_date = datetime.datetime.now().strftime("%Y%m%d")
name_process = V_PROCESS_MAPEO
path_log = V_PATH_LOG
filename = V_PATH_INPUT + "/" + p_file
path_mapping = V_PATH_MAPPING

#GENERAR ARCHIVO DE MAPEO
path_filename_xml_1 = path_mapping + '/' + p_file


# CREANDO DIRECTORIO LOG PARA LA FECHA ACTUAL
path_log_current_date = path_log + '/' + current_date + '/'
if not os.path.exists(path_log_current_date):
    os.makedirs(path_log_current_date, 0o777)  # CREA LA CARPETA Y ASIGNA LOS PERMISOS
    print_with_logging("Se creo el directorio: " + path_log_current_date, 'info')

process_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
file_log = path_log_current_date + name_process + '_' + process_time + '.log'

# SE CREA LOG DE EJECUCION
# RESETEAR LOS HANDLERS DEL LOGGING
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename=file_log, filemode="w", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print_with_logging('Inicio de Ejecucion del proceso', 'info')
print_with_logging('Nombre del proceso: ' + name_process, 'info')
print_with_logging('Ruta Log: ' + path_log, 'info')
print_with_logging('Nombre del Archivo: ' + filename, 'info')

# INICIO DE PROCESO DE MAPEO
print_with_logging('Inicio de proceso de mapping de XML', 'info')

try:

    #LEER ARCHIVO QUE CONTIENE EL XML
    tree = ET.parse(filename)
    root = tree.getroot()

    #CONFIGURACIÓN DE NAMESPACES
    ns = {'soapenv':'http://schemas.xmlsoap.org/soap/envelope/',
          'head':'http://telefonica.com/globalIntegration/header',
          'body':'http://telefonica.com/globalIntegration/services/cancelTroubleTicket/v1'}

    #MAPEO DE LOS TAGs
    envelope = ET.Element('soapenv:Envelope', attrib={'xmlns:soapenv':'http://schemas.xmlsoap.org/soap/envelope/','xmlns:head':'http://telefonica.com/globalIntegration/header','xmlns:v1':'http://telefonica.com/globalIntegration/services/modifyTroubleTicket/v1'})

    header1 = ET.SubElement(envelope, 'soapenv:Header')
    body = ET.SubElement(envelope, 'soapenv:Body')

    #HEADER
    headerIn = ET.SubElement(header1, 'head:HeaderIn')
    country = ET.SubElement(headerIn, 'head:country')
    lang = ET.SubElement(headerIn, 'head:lang')
    entity = ET.SubElement(headerIn, 'head:entity')
    system = ET.SubElement(headerIn, 'head:system')
    subSystem = ET.SubElement(headerIn, 'head:subsystem')
    originator = ET.SubElement(headerIn, 'head:originator')
    userId = ET.SubElement(headerIn, 'head:userId')
    operation = ET.SubElement(headerIn, 'head:operation')
    pid = ET.SubElement(headerIn, 'head:pid')
    execId = ET.SubElement(headerIn, 'head:execId')
    msgId = ET.SubElement(headerIn, 'head:msgId')
    timeStamp = ET.SubElement(headerIn, 'head:timestamp')
    msgType = ET.SubElement(headerIn, 'head:msgType')

    #BODY
    canTroubleTicketReq = ET.SubElement(body, 'v1:cancelTroubleTicketRequest')
    interactionDate = ET.SubElement(canTroubleTicketReq, 'v1:interactionDate')
    id = ET.SubElement(canTroubleTicketReq, 'v1:ID')
    externalId = ET.SubElement(canTroubleTicketReq, 'v1:externalId')
    relObjList = ET.SubElement(canTroubleTicketReq, 'v1:relatedObjectList')

    #OBTENER LOS DATOS HEADER DEL XML
    for item_header in root.findall('./soapenv:Header', ns):
      #print(2)
      for item_headerIn in item_header.findall('./head:HeaderIn', ns):
        #print(3)
        in_country = item_headerIn.find('head:country',ns).text
        in_lang = item_headerIn.find('head:lang',ns).text
        in_entity = item_headerIn.find('head:entity',ns).text
        in_system = item_headerIn.find('head:system',ns).text
        in_subSystem = item_headerIn.find('head:subsystem',ns).text
        in_originator = item_headerIn.find('head:originator',ns).text
        in_userId = item_headerIn.find('head:userId',ns).text
        in_operation = item_headerIn.find('head:operation',ns).text
        ##in_pid = item_headerIn.find('head:pid',ns).text  EJEMPLO NO TRAE
        in_pid = '' if (item_headerIn.find('head:pid', ns) == None) else item_headerIn.find('head:pid', ns).text
        in_execId = item_headerIn.find('head:execId',ns).text
        ##in_msgId = item_headerIn.find('head:msgId',ns).text
        in_msgId = '' if (item_headerIn.find('head:msgId', ns) == None) else item_headerIn.find('head:msgId', ns).text
        in_timeStamp = item_headerIn.find('head:timestamp',ns).text
        ##in_msgType = item_headerIn.find('head:msgType',ns).text
        in_msgType = '' if (item_headerIn.find('head:msgType', ns) == None) else item_headerIn.find('head:msgType', ns).text

        country.text = in_country
        lang.text = in_lang
        entity.text = in_entity
        system.text = in_system
        subSystem.text = in_subSystem
        originator.text = in_originator
        userId.text = in_userId
        operation.text = in_operation
        pid.text = in_pid
        execId.text = in_execId
        msgId.text = in_msgId
        timeStamp.text = in_timeStamp
        msgType.text = in_msgType
        
        
    #OBTENER LOS DATOS BODY DEL XML
    for item_body in root.findall('./soapenv:Body', ns):
      #print(4)
      for item_mttr in item_body.findall('./body:cancelTroubleTicketRequest',ns):
        #print(5)
        in_interactionDate = item_mttr.find('body:interactionDate',ns).text
        in_externalId = item_mttr.find('body:externalId',ns).text
        externalId.text = in_externalId
        interactionDate.text = in_interactionDate
        #relatedObjectList
        for item_relObjList in item_mttr.findall('./body:relatedObjectList', ns):
          #print(7)
          # detalle RelatedObject
          for item_relObj in item_relObjList.findall('./body:RelatedObject', ns):
            #print(8)
            #relObj = ET.SubElement(relObjList, 'v1:RelatedObject')
            relObject = ET.SubElement(relObjList, 'v1:RelatedObject')
            involvement = ET.SubElement(relObject, 'v1:involvement')  
            describeByList = ET.SubElement(relObject, 'v1:describeByList')
            # values 
            in_involvement = item_relObj.find('body:involvement',ns).text
            involvement.text = in_involvement
            
            # describeByList
            for item_desLst in item_relObj.findall('./body:describeByList',ns):
              #print(9)
              # detalle Characteristic
              for item_char in item_desLst.findall("./body:Characteristic",ns):
                #print(10)
                # metadata
                characteristic = ET.SubElement(describeByList, 'v1:Characteristic')
                charName = ET.SubElement(characteristic, 'v1:name')
                charValue = ET.SubElement(characteristic, 'v1:value')
                # values
                in_charName = item_char.find('body:name',ns).text
                in_charValue = item_char.find('body:value',ns).text
                charName.text = in_charName
                charValue.text = in_charValue

    #se va poner un prefijo con el filename_mapping
    tree = ET.ElementTree(envelope)
    tree.write(path_filename_xml_1)
    
    print_with_logging('Se culmina correctamente el proceso de mapping del XML: ' + path_filename_xml_1, 'info')
except Exception as e:
    print_with_logging('Ocurrio un error: Revisar el error en la carpeta ' + file_log, 'error')
    logging.error('Detalle: ', exc_info=e)
    print_with_logging('Fin de proceso de mapping del XML', 'info')
    sys.exit(1)

print_with_logging('Fin de proceso de mapping del XML', 'info')