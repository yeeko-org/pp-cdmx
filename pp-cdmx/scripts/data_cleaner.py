# -*- coding: utf-8 -*-
import re
from geographic.models import *
from difflib import SequenceMatcher
import unidecode
from public_account.models import *
from period.models import *
import numpy
from vision.get_columns import get_year_data
import json
from pprint import pprint

def cleanSuburbName(text):
    try:
        final_name = unidecode.unidecode(text).upper()
    except Exception as e:
        print e
        final_name = text
    #Sustituimos el signo "OR" (|) por I latina
    final_name = re.sub(r'(\|)', 'I', final_name)
    final_name = re.sub(r'[^0-9a-zA-Z\s\(\)\|\_]', '', final_name)
    final_name = final_name.upper()
    #Sustituimos puntos por espacios
    final_name = re.sub(r'\.', ' ', final_name)
    final_name = final_name.strip()
    #eliminamos espacios entre paréntesis ( U HAB ) --> (U HAB)
    final_name = re.sub(r'\(\s?(\D*)\s?\)', r'(\1)', final_name)
    #Eliminamos la clave en el normal_name
    re_cve = re.compile(r'(\(?\s?\d{2})\s?\D?\s?(\d{3}\s?\)?)')
    final_name = re.sub(re_cve, '', final_name)
    #compact_name = re.sub(r'[^0-9A-Z]', '', final_name)
    return final_name

def buildSuburbComparename():
    all_suburbs = Suburb.objects.all()
    for sub in all_suburbs:
        sub.short_name=cleanSuburbName(sub.name)
        sub.save()

def calculateSuburb(data_subs, image):
    column_values = []
    #Antes que nada, validamos que sea una columna válida:
    #total_words = 0
    suburbs = Suburb.objects.filter(townhall=image.public_account.townhall)
    seq = 0 
    raw_collection = []
    need_jump = False
    for meta in data_subs["data"]:
        for row in meta:
            raw_collection.append(row)

    for idx_raw, row in enumerate(raw_collection):
        if need_jump:
            need_jump = False
            continue

        can_be_comb = True
        type_comb = None
        sub_id = None
        try:
            after_base = raw_collection[idx_raw+1]
            comb_base = "%s %s"%(row, after_base)
        except Exception as e:
            print "no hay siguiente"
            after_base = False
        curr = get_data_suburb(row, suburbs, image)

        if curr["name"] == False:
            continue
        #El extraño caso:
        elif curr["id"] and curr["cve"] and curr["id"] != curr["cve"]:
            image.set_new_error("%s row: %s"%(
                u"Se encontraron dos claves en el mismo lugar", row))
            type_comb = 'error'
        #El registro tiene sentido en sí mismo:
        elif curr["id"] and curr["id"] == curr["cve"]:
            after_base = False
            type_comb = 'curr'
        #Si se pudo obtener el siguient registro:
        elif after_base:
            after = get_data_suburb(after_base, suburbs, image)
            comb = get_data_suburb(comb_base, suburbs, image)

            #Si lo siguiente no tiene nombre, preveer saltar
            if not after["name"]:
                need_jump = True

            #Cuando el siguiente registro tiene sentido por sí mismo:
            if after["id"]:
                can_be_comb = False
            else:
                #Los siguientes casos asument que hay ID actual:
                if curr["id"]:
                    #La clave del siguiente coincide con el nombre actual
                    if curr["id"] == after["cve"]:
                        type_comb = 'comb'
                    #La clave del siguiente no coincide con el nombre actual
                    elif after["cve"] and curr["id"] != after["cve"]:
                        type_comb = 'curr'
                    #La clave del siguiente no coincide con el nombre combinado
                    elif after["cve"] and comb["id"] != after["cve"]:
                        type_comb = 'curr'
                if curr["cve"] and not type_comb:
                    #la clave actual coincide con el texto combinado:
                    if comb["id"] == curr["cve"]:
                        type_comb = 'comb'
                    #Si el siguiente también tiene clave
                    elif after["cve"]:
                        type_comb = 'curr'
                if comb["id"] and not type_comb:
                    #La clave del siguiente coincide con el nombre combinado
                    if comb["id"] == comb["cve"]:
                        type_comb = 'comb'
                #Cuando el siguiente registro tiene una clave:
                elif not curr["id"] and not curr["cve"] and after["cve"]:
                    try:
                        sub_name = suburbs.get(id=after["cve"]).short_name
                    except Exception as e:
                        image.set_new_error("%s%s id: "%(u"Había cve sig pero" 
                            " no lo hallamos", after["cve"]))
                        sub_name= ""
                    comb_coinc = similar(comb["name"], sub_name)
                    after_coinc = similar(after["name"], sub_name)
                    if  0.5 < comb_coinc > after_coinc:
                        type_comb='comb'
                        sub_id = after["cve"]
                    else:
                        can_be_comb = False

        else:
            can_be_comb = False


        if type_comb != 'error':
            if type_comb != 'comb' and not sub_id:
                sub_id = curr["cve"] or curr["id"]    
                if sub_id:
                    type_comb == 'curr'
                    can_be_comb = False
            if can_be_comb and not sub_id:
                sub_id = comb["cve"] or comb["id"]
                if sub_id:
                    type_comb == 'comb'
            if type_comb == 'comb':
                need_jump = True
            if sub_id:
                try:
                    column_values[-1]["can_be_comb"] = False
                except Exception as e:
                    print "no se puede setear el previo"
    
        if sub_id:
            sub_id = saveFinalProjSuburb(sub_id, image)

        if sub_id and not type_comb:
            type_comb = 'curr'
            can_be_comb = False


        new_dict = {"seq": seq,
                    "suburb_id": sub_id,
                    "image_id": image.id,
                    "type_comb": type_comb,
                    "can_be_comb": can_be_comb,
                    "curr": curr["name"],
                    "curr_raw": row}
        if after_base and type_comb != "error":
            new_dict["after"] = after["name"]
            new_dict["comb"] = comb["name"]
            new_dict["comb_raw"] = comb_base
        seq+=1
        column_values.append(new_dict)
    return column_values

def get_data_suburb(row, suburbs, image):
    if not row:
        return {"name": None, "id": None, "cve":None}
    data_dict = {}
    name = get_normal_name(row)
    data_dict["name"] = name
    data_dict["cve"] = get_cve(row, suburbs) if name else None
    data_dict["id"] = get_suburb_id(name, suburbs, image) if name else None
    return data_dict


def get_normal_name(row):
    normal_name = cleanSuburbName(row)
    raw_non_spaces = len(re.sub(r'[^\w]', '', normal_name))
    #Validadores para excluir palabras que ya conocemos
    if bool(re.search(
        r'(COLONIA O PUEBLO|PUEBLO ORIGINARIO|UNIDAD RESPON)', normal_name)):
        return False
    #Esto significa que llegamos al final
    elif bool(re.search(r'(REFIERE|REMANENTE|TOTAL|AUTORI|ELABORO|LABORADO)',
        normal_name)):
        return False
    #En el caso de que se coma letras de otra columna
    elif raw_non_spaces < 4:
        return None
    return normal_name

#import re
#row = "sdsadf 54-323 saf "

def get_cve(row, suburbs):
    #identificamos el format (11-034)
    re_has_cve = re.compile(r'.*(?:\D|^)(\d{2})\s?\D?\s?(\d{3})(?:\D|$).*')
    #Se busca la clave de la colonia
    cve_suburb = None
    sub_id = None
    if re.match(re_has_cve, row):
        cve_suburb = re.sub(re_has_cve, r'\1-\2', row)
        if int(cve_suburb[:2]) < 17:
            try:
                sub_id = suburbs.get(cve_col=cve_suburb).id
            except Exception as e:
                print 'Clave no encontrada'+cve_suburb
    return sub_id


def get_suburb_id(normal_name, suburbs, image):
    sub_id = None
    subs_found = suburbs.filter(short_name=normal_name,
        finalproject__period_pp=image.public_account.period_pp,
        finalproject__image__isnull=True)
    if subs_found.count() > 1:
        image.set_new_error("%s id: "%(
            u"Se encontraron vario suburbs con el name", normal_name))
    elif subs_found.count()  == 1:
        return subs_found.first().id
    else:
        return None

def similar(a, b):
    if a and b:
        return SequenceMatcher(None, a, b).ratio()
    else:
        return 0


def saveFinalProjSuburb(sub_id, image):
    from project.models import FinalProject
    try:
        final_proy = FinalProject.objects.get(suburb__id=sub_id,
            image__isnull=True)
        final_proy.image = image
        final_proy.save()
        return sub_id
    except Exception as e:
        print "había ID pero no encontramos FinalProject"
        #print normal_name
        return None


def calcColumnsNumbers(data_numbers, th_short=None):
    column_values = []
    large_row = 0
    #seq = 0
    column_number = 1 
    current_len = 0
    len_array = []
    is_incomplete = False
    collects, numbers_count = clean_no_numbers(data_numbers["data"])
    media_rows = numbers_count / 5


    for idx, rows in enumerate(collects):
        is_ammount = (column_number > 1 and column_number < 5)
        #seq+=1
        the_dict = calculateNumbers(rows, is_ammount)
        if the_dict:
            len_dict = len(the_dict)
            current_len+=len_dict
            if not large_row and current_len + 2 >= media_rows:
                large_row = current_len

            if is_incomplete:
                column_values[-1]+=the_dict
                is_incomplete = False
            else:
                column_values.append(the_dict)
            try:
                can_add_next = len(collects[idx+1]) + current_len <= large_row
            except Exception as e:
                can_add_next = False
            if current_len + 2 >= large_row and large_row and not can_add_next:
                column_number+=1
                len_array.append(current_len)
                current_len = 0
            else:
                is_incomplete = True
            #column_values[column_number-1]=the_dict
        else:
            print u"no hay the_dict aunque ya haya pasado la verificación"
    return column_values, len_array

def clean_no_numbers(collects):
    new_collects = []
    numbers_count = 0
    for rows in collects:
        new_row = []
        for value in rows:
            new_value = value
            #Sustituimos las Bs por 8
            new_value = re.sub(r'(B)', '8', new_value)
            #Sustituimos las Os por 0
            new_value = re.sub(r'(O)', '0', new_value)
            #identificamos títulos
            if re.match(r'3\s?\/\s?1', new_value):
                print "es el título 3/1"
                continue
            #Sustituimos los diagonales por comas
            new_value = re.sub(r'(/)', ',', new_value)
            #Nos quedamos solo con lo que utilizaremos
            words_and_dig_count = len(re.sub(r'[^\w]', '', new_value))    
            #Solo los Números
            digits_count = len(re.sub(r'[^\d]', '', new_value))
            #La mayor parte que sean los números
            try:
                if (digits_count / float(words_and_dig_count)) < 0.8:
                    #print "casi todos son letras"
                    continue
            except Exception as e:
                print e
                continue
            new_value = re.sub(r'[^0-9\,\.\s\-\%\(\)]', '', new_value)
            #números y letras, no más:
            #Limpieza básica de espacios:
            new_value = new_value.strip()
            #Se quitan los espacios alrededor de puntos y comas (siempre a puntos)
            # 4 , 5 --> 4,5
            new_value = re.sub(r'(\d)\s?[\.\,]\s?(\d)', '\\1.\\2', new_value)
            new_row.append(new_value)
            numbers_count+=1
        if len(new_row):
            new_collects.append(new_row)
    return new_collects, numbers_count


def calculateNumbers(rows, is_ammount, seq=None):
    #### Variables que nos ayudarán:
    # Patrón REGEX para porcentajes válidos.
    #re_ammount = re.compile(
        #r'^(\d[\,\.](?=\d{3}))?(\d{1,3}[\,\.](?=\d{3}))?(\d{1,3})(\.\d{2})?$')
    re_ammount = re.compile( r'^\d{1,7}(\.\d{2})?$')
    re_percent = re.compile( r'^\-?\d{1,3}(\.\d{1,2})?[489%]?\)?$')
    re_compara = re_ammount if is_ammount else re_percent
    has_percent = re.compile(r'[489%]$')
    has_decimals = re.compile(r'\d{2}$')
    re_format = has_decimals if is_ammount else has_percent    
    column_values = []
    count_special_format = 0
    has_special_format = False
    for row in rows:
        new_value = row
        
        if not is_ammount:
            #Se quita el espacio entre el número y el porcentaje, en caso de existir.
            new_value = re.sub(r'(\d)\s?%', '\\1%', new_value)
            #Se quitan los espacios después del abrir paréntesis y antes de cerrarlos
            new_value = re.sub(r'\(\s?(.*)(\S+)\s?\)', '(\\1\\2)', new_value)
            # new_value = re.sub(r'\(\s?(.+)\s?\)', '\\1', new_value)
        else:
            #Si después de los puntos hay 3 caracteres, los eliminamos:
            new_value = re.sub(r'\.(\d{3})', '\\1', new_value)
        #Se separan los números que estén en el mismo elemento
        if (is_ammount and len(re.sub(r'[^\d]', '', new_value)) < 10 
            and len(re.sub(r'[^\1-9]', '', new_value)) > 2):
            new_value = re.sub(r'[^\d\.]', '', new_value)
        splited = re.split(r'\s', new_value)
        for unity in splited:
            #Se cuentan si tiene el formato percent o decimal
            count_special_format+= 1 if bool(re_format.search(unity)) else 0
            ref_objs = {"raw_unity": unity}
            #Se busca si tienen alguno de los formatos posibles:
            ref_objs["correct_format"] = bool(re_compara.search(unity))
            if (len(splited)>1):
                ref_objs["raw_origin"] = row
            column_values.append(ref_objs)
    #Si la mayoría tienen el formato porcentaje, asumimos que todos lo tienen:
    len_column = len(column_values)
    if len_column:
        has_special_format = count_special_format / float(len_column) >= 0.75
    else:
        return False
    for new_value in column_values:
        if new_value["correct_format"]:
            only_ints = new_value["raw_unity"]
            if (has_special_format and not is_ammount):
                only_ints = re.sub(re_format, '', only_ints)
            if not only_ints:
                continue
            try:
                float_value=float(only_ints)
            except Exception as e:
                only_ints = re.sub(re_format, '', only_ints)
                float_value=float(only_ints)
            if is_ammount and 0<float_value<1000 or float_value > 10000000:
                column_values.remove(new_value)
                continue
            new_value["final_value"] = float_value
    #print column_values
    return column_values