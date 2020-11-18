# -*- coding: utf-8 -*-
import re
from geographic.models import *
from public_account.models import *
from period.models import *
import numpy
from vision.get_columns import get_year_data
import json
from pprint import pprint

#Esta función hace una estandarización y limpieza de nombres para facilitar 
#encontrar similitudes entre los nombres oficiales y los que ponen las alcaldías
def cleanSuburbName(text):
    import unidecode
    #Primero estandarizamos los carácteres de español como acentos o eñes
    try:
        final_name = unidecode.unidecode(text).upper()
    except Exception as e:
        print e
        final_name = text.upper()
    #Sustituimos el signo "OR" (|) por I latina
    final_name = re.sub(r'(\|)', 'I', final_name)
    #Nos vamos a quedar con números, letras espacios y muy pocos otros 
    #caracteres: guiones bajos y diagonales (slashs) por que con ellos se
    #distinguen algunas colonias. Lo demás, simplemento lo eliminamos:
    final_name = re.sub(ur'[^0-9A-Z\s\(\)\_\-\/\º\.\,]', '', final_name)    
    final_name = final_name.upper()
    #Sustituimos puntos, comas y guiones por espacios, lo cuales se añaden sin
    #ningún patrón y sólo contribuyen a reducir el nivel de coincidencia.
    final_name = re.sub(r'[\.\,\-]', ' ', final_name)
    #quitamos dobles espacios
    final_name = re.sub(r' +', ' ', final_name)
    #eliminamos espacios entre paréntesis , ej: ( U HAB ) --> (U HAB)
    final_name = re.sub(r'\(\s?', r'(', final_name)
    final_name = re.sub(r'\s?\)', r')', final_name)
    #Algunos remplazos comunes de alternativas de nombramiento:
    re_uhab = re.compile(r'\(\s?(CONJ HAB|UNIDAD HABITACIONAL|U HABS|CONJUNTO HABITACIONAL)\s?\)')
    final_name = re.sub(re_uhab, r'(U HAB)', final_name)
    final_name = re.sub(r'\(\s?(FRACCIONAMIENTO)\s?\)', '(FRACC)', final_name)
    final_name = re.sub(ur'\(\s?(AMPLIACION|AMPLIACIÓN)\s?\)', '(AMPL)', final_name)
    #Eliminamos la clave en el normal_name (se hace un análisis aparte)
    #La clave de las colonias tiene el formato DD-AAA donde DD es la clave de
    #la alcaldía a dos dígitos AAA es la de la colonia a 3 dígitos.
    #El divisor, el OCR lo puede traducir como cualquier caracter no numérico.
    re_cve = re.compile(r'(\(?\d{2})\s?\D?\s?(\d{3}\)?)')
    final_name = re.sub(re_cve, '', final_name)
    #quitamos espacios al principio y al final
    final_name = final_name.strip()
    #quitamos dobles espacios, de nuevo
    final_name = re.sub(r' +', ' ', final_name)
    return final_name


def calculateSuburb_v2(text, maybe_cve, image):
    suburbs = Suburb.objects.filter(townhall=image.public_account.townhall)
    errors = []
    #Es el id de la alcaldía con la cual se encontró una coincidencia.
    sub_id = None

    #normal_name --> nombre normalizado
    normal_name = get_normal_name(text)
    #Si el nombre no se puede normalizar o es válido, cancelamos la línea.
    if not normal_name:
        return False, normal_name, errors
    
    #cve --> El id de la Colonia (Suburb) que haya coincidido si se encontró
    # una clave y si coincidió esa clave con lo que había en base de datos.
    cve = get_cve(text, suburbs)
    #Id es el ID de la colonia que encontró a partir del nombre normalizado.
    sub_id = get_suburb_id(normal_name, suburbs, image)

    #El extrañísimo (pero siempre es posible) caso de que existan dos 
    # alcaldías distintas en el mismo lugar.
    if sub_id and cve and sub_id != cve:
        errors.append("Dos claves en el mismo lugar")
        set_new_error(image, "%s row: %s"%(
            u"Se encontraron dos claves en el mismo lugar: ", text))
        return None, normal_name, errors
    cve_in_proj = get_cve(maybe_cve, suburbs)
    #Se devuelve la primera coincidencia:
    return cve or sub_id or cve_in_proj, normal_name, errors

def get_normal_name(text):
    normal_name = cleanSuburbName(text)
    raw_non_spaces = len(re.sub(r'[^\w]', '', normal_name))
    #Validadores para excluir palabras que ya conocemos y que sabemos que 
    #son parte de los encabezados o de los pie de página y no contienen datos.
    if bool(re.search(
        r'(COLONIA O PUEBLO|ORIGINARIO|UNIDAD RESPON)', normal_name)):
        return False
    #Esto significa que llegamos al final, son palabras que no están en ninguna
    # colonia y siempre están en el pie de página.
    elif bool(re.search(r'(REFIERE|REMANENTE|TOTAL|AUTORI|ELABORO|LABORADO|DIRECTOR)',
        normal_name)):
        return False
    #Ninguna Colonia tiene un nombre tan corto, entonces devolvemos un None 
    # para saber que por sí misma no puede ser una colonia, es el caso de que
    # se coma letras de otra columna
    elif raw_non_spaces < 4:
        return None
    return normal_name

def get_cve(text, suburbs):
    cve_suburb = None
    sub_id = None
    #identificamos el formato (11-034)
    re_has_cve = re.compile(r'.*(?:\D|^)(\d{2})\s?\D?\s?(\d{3})(?:\D|$).*')
    #Se busca la clave de la colonia
    if re.match(re_has_cve, text):
        #Normalizamos el formato para aquello que "parece" clave
        cve_suburb = re.sub(re_has_cve, r'\1-\2', text)
        #sabemos que el id de la alcaldía sólo llega a 16, descartamos lo que
        # sea más grande que eso
        if int(cve_suburb[:2]) < 17:
            try:
                sub_id = suburbs.get(cve_col=cve_suburb).id
            except Exception as e:
                print 'Clave no encontrada'+cve_suburb
    return sub_id


def get_suburb_id(normal_name, suburbs, image):
    sub_id = None
    #La búsqueda se hace entre las Colonias que no han tenido coincidencias,
    # para no repetir dos registros idénticos.
    subs_found = suburbs.filter(short_name=normal_name,
        finalproject__period_pp=image.public_account.period_pp,
        finalproject__image__isnull=True)
    if subs_found.count() > 1:
        set_new_error(image, "%s id: "%(
            u"Se encontraron varios suburbs con el name", normal_name))
    elif subs_found.count()  == 1:
        return subs_found.first().id
    else:
        return None

def similar(a, b):
    from difflib import SequenceMatcher
    if a and b:
        return SequenceMatcher(None, a, b).ratio()
    else:
        return 0


def saveFinalProjSuburb_v2(sub_id, row_data, simil=1):
    from public_account.models import column_types, PPImage
    from classification.models import Anomaly
    from project.models import FinalProject, AnomalyFinalProject
    image = PPImage.objects.get(id=row_data["image_id"])
    try:
        final_proy = FinalProject.objects.get(suburb__id=sub_id,
            image__isnull=True)
        final_proy.image = image
        final_proy.similar_suburb_name = simil
        for idx, value in enumerate(row_data):
            if idx:
                print column_types[idx]["field"]
                final_proy[column_types[idx]["field"]] = value
        final_proy.save()
        for error in row_data["errors"]:
            anomaly, created = Anomaly.objects\
                .get_or_create(name=error, is_public=False)
            AnomalyFinalProject.objects.create(
                final_project=final_proy, anomaly=anomaly)
        return sub_id, []
    except Exception as e:
        set_new_error(image, "El ID %s no lo encontramos en FinalProject"%sub_id)
        print "asd"
        print e
        return None, ["sub_id no encontrado"]

def calculateNumber(text, column, has_special_format=None):
    errors = []
    is_ammount = column["type"] = "ammount"

    new_value = text
    #Sustituimos las Bs por 8
    new_value = re.sub(r'(B)', '8', new_value)
    #Sustituimos las Os por 0
    new_value = re.sub(r'(O)', '0', new_value)
    #Quitamos los paréntesis que hacen ruido con (100)  y (1)
    new_value = re.sub(r'[\(\)]', '', new_value)
    #Sustituimos las Ss por 5
    new_value = re.sub(r'(s|S)', '5', new_value)
    #Sustituimos los diagonales por comas
    new_value = re.sub(r'(/)', ',', new_value)
    #Nos quedamos con números y algunas letras, no más:
    new_value = re.sub(r'[^0-9\,\.\s\-\%\(\)]', '', new_value)
    #Limpieza básica de espacios:
    new_value = new_value.strip()
    #Se quitan los espacios alrededor de puntos y comas (siempre a puntos)
    # 4 , 5 --> 4,5
    new_value = re.sub(r'(\d)\s?[\.\,]\s?(\d)', '\\1.\\2', new_value)

    # Patrón REGEX para números (montos) válidos.
    re_ammount = re.compile( r'^\d{1,7}(\.\d{2})?$')
    # Patrón REGEX para porcentajes válidos.
    re_percent = re.compile( r'^\-?\d{1,3}(\.\d{1,2})?[4895%]?\)?$')
    re_compara = re_ammount if is_ammount else re_percent
    has_percent = re.compile(r'[4895%]$')
    has_decimals = re.compile(r'\d{2}$')
    re_format = has_decimals if is_ammount else has_percent    
    
    ### column_values = []

    
    if not is_ammount:
        #Se quita el espacio entre el número y el porcentaje, en caso de existir.
        new_value = re.sub(r'(\d)\s?%', '\\1%', new_value)
        #Se quitan los espacios después del abrir paréntesis y antes de cerrarlos
        new_value = re.sub(r'\(\s?(.*)(\S+)\s?\)', '(\\1\\2)', new_value)
        # new_value = re.sub(r'\(\s?(.+)\s?\)', '\\1', new_value)
    else:
        #Si después de los puntos hay 3 caracteres, los eliminamos,
        #con la idea de dejar máximo un punto decimal
        new_value = re.sub(r'\.(\d{3})', '\\1', new_value)

    #Se busca si tienen alguno de los formatos posibles:
    correct_format = bool(re_compara.search(new_value))

    #si se trata de un simple conteo de formatos especiales:
    if has_special_format == None:
        if not correct_format:
            return None
        return 1 if bool(re_format.search(new_value)) else 0

    if not correct_format:
        errors.append(u"Formato incorrecto en columna %s"%column["title"])
    only_ints = new_value
    #Limpieza de porcentajes
    if (has_special_format and not is_ammount):
        only_ints = re.sub(re_format, '', only_ints)
    #Forzamos un número flotante para su procesamiento como número
    try:
        float_value=float(only_ints)
    except Exception as e:
        only_ints = re.sub(re_format, '', only_ints)
        try:
            float_value=float(only_ints)
        except Exception as e:
            print "error al convertir en calculateNumber en text: \"%s\""%text
            print e
            float_value=0
    #Algunos números que si los obtenemos, significa un problema
    if (is_ammount and 0 < float_value < 1000) or float_value > 10000000:
        errors.append(u"Número inválido en columna %s"%column["title"])
    elif not is_ammount and float_value > 2:
        float_value = float_value/float(100)
    return float_value, errors



def flexibleMatchSuburb_v2(orphan_rows, pa):
    from scripts.data_cleaner import similar
    from pprint import pprint
    from difflib import SequenceMatcher
    print u"------------------------------------"
    # print orphan_rows
    new_orphans = []
    missing_row_idxs = [idx for idx, x in enumerate(orphan_rows)]
    missings_subs = Suburb.objects.filter(
        townhall=pa.townhall,
        finalproject__period_pp=pa.period_pp,
        finalproject__image__isnull=True)
    for sub in missings_subs:
        max_conc = 0
        sub_id = None
        final_row_idx = -1
        for row_idx in missing_row_idxs:
            #if orphan_rows[row_idx]["invalid"]:
                #continue
            concordance = SequenceMatcher(None, sub.short_name, 
                orphan_rows[row_idx]["data"][0]).ratio()
            # print "%s -- %s"%(may, concordance)
            if concordance > 0.8 and concordance > max_conc:
                final_row_idx = row_idx
                max_conc = concordance
        if final_row_idx > -1:
            # print final_row_idx
            sel_row = orphan_rows[final_row_idx]
            sub_id = saveFinalProjSuburb_v2(sub.id, sel_row, max_conc)
            missing_row_idxs.remove(row_idx)
            # print "-------------"
            # print sub_id
    final_missings_subs = Suburb.objects.filter(
        townhall=pa.townhall,
        finalproject__period_pp=pa.period_pp,
        finalproject__image__isnull=True)
    new_orphans = []
    if len(final_missings_subs):
        for miss_idx in missing_row_idxs:
            new_orphans.append(orphan_rows[miss_idx])

    pa.orphan_rows = json.dumps(new_orphans)
    pa.save()
    return new_orphans

def set_new_error(model, text_error):
    current_notes = model.error_cell
    #print text_error
    if current_notes:
        model.error_cell = "%s\n%s"%(current_notes, text_error)
    else:
        model.error_cell = text_error
    model.save()
