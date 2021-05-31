# -*- coding: utf-8 -*-
import re
import numpy
import json


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
    final_name = re.sub(ur'^(COMITE|COMITÉ|COLONIA)\s', '', final_name)
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

def calculateNumber(text, column, has_special_format=None):
    errors = []
    is_ammount = column["type"] == "ammount"

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
    #por si se trata de una división entre 0 impresa
    has_error_excel = bool(re.search(r'D.V', new_value))
    #Nos quedamos con números y algunas letras, no más:
    new_value = re.sub(r'[^0-9\,\.\-\%]', '', new_value)
    ##Limpieza básica de espacios:
    ##new_value = new_value.strip()
    ##Se quitan los espacios alrededor de puntos y comas (siempre a puntos)
    ## 4 , 5 --> 4,5
    ##new_value = re.sub(r'(\d)\s?[\.\,]\s?(\d)', '\\1.\\2', new_value)
    #Se sustituyen las comas por puntos
    new_value = re.sub(r'(\,)', '.', new_value)
    # Patrón REGEX para números (montos) válidos.
    re_ammount = re.compile( r'^\d{1,7}(\.\d{2})?$')
    # Patrón REGEX para porcentajes válidos.
    re_percent = re.compile( r'^\-?\d{1,3}(\.\d{1,2})?[4895%]?\)?$')
    re_compara = re_ammount if is_ammount else re_percent
    has_percent = re.compile(r'[4895%]$')
    has_decimals = re.compile(r'\d{2}$')
    re_format = has_decimals if is_ammount else has_percent    
    
    ##if not is_ammount:
        ##Se quita el espacio entre el número y el porcentaje, en caso de existir.
        ##new_value = re.sub(r'(\d)\s?%', '\\1%', new_value)
        ##Se quitan los espacios después del abrir paréntesis y antes de cerrarlos
        ##new_value = re.sub(r'\(\s?(.*)(\S+)\s?\)', '(\\1\\2)', new_value)
        ##new_value = re.sub(r'\(\s?(.+)\s?\)', '\\1', new_value)
    ##else:
    if is_ammount:
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
        if has_error_excel and not is_ammount:
            new_value = '0%' if has_special_format else '0'
        else:
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
            errors.append(u"No se pudo converir número en columna %s"%column["title"])
            if only_ints:
                try:
                    print "error al convertir en calculateNumber: \"%s\""%text
                except Exception as e:
                    pass
                print e
            return None, errors
    #Algunos números que si los obtenemos, significa un problema
    if (is_ammount and 0 < float_value < 1000) or float_value > 10000000:
        errors.append(u"Número inválido en columna %s"%column["title"])
    elif not is_ammount and float_value > 2:
        float_value = float_value/float(100)
    return float_value, errors


def calculate_special_formats_v3(pa, all_images, columns_nums, image_num):
    variables = pa.get_variables()
    # si ya se había canculado el special_formats, simplemente se obtiene
    # if "special_formats" in variables:
    #     return variables["special_formats"]

    # si no, se calcula:
    # Se trabajará solo con las columnas numéricas, que son las últimas 5
    count_rows = [0, 0, 0, 0, 0]
    special_format_count = [0, 0, 0, 0, 0]
    special_formats = [False, False, False, False, False]
    for image in all_images[:3]:
        for row in image.get_table_data():
            # Se trabajarán solo con los las últimas 5 columnas
            for idx, value in enumerate(row[3:]):
                sum_col = calculateNumber(value, columns_nums[idx])
                # Solo se sumarán si la función arrojó algún número
                if sum_col is not None:
                    special_format_count[idx] += sum_col
                    count_rows[idx] += 1

        # Se puede detarminar una tendencia de tener algún formato
        # especial si existen al menos 5 datos con formato válido
    for idx, col in enumerate(columns_nums):
        curr_tot = float(count_rows[idx])
        is_special = special_format_count[idx]/curr_tot >= 0.75 if curr_tot else False
        special_formats.append(is_special)
    variables["special_formats"] = special_formats
    pa.variables = json.dumps(variables)
    pa.save()
    return special_formats


from project.models import FinalProject
from public_account.models import PublicAccount, PPImage


def clean_text(text):
    # final_text = unidecode.unidecode(text)
    final_text = text
    final_text = final_text.strip()
    final_text = re.sub(r' +', ' ', final_text)
    final_text = re.sub(r'(\(|\¿|\¡)\s?', '\\1', final_text)
    final_text = re.sub(r'\s?(\)|\:|\,|\.|\;|\?|\!)', '\\1', final_text)
    final_text = re.sub(r'(\)|\:|\,|\.|\;|\?|\!)(\w)', '\\1 \\2', final_text)
    final_text = final_text.strip()
    return final_text