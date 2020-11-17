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

#Esta funcion es para encontrar las coincidencias de cada columna, asumiendo
#que ya tenemos los datos de una sola columna.
#Un poco de contexto:
# Las colonias pueden estar en una, dos o tres líneas, y pueden contener
# o no la clave de la alcaldía.
def calculateSuburb(data_subs, image):
    column_values = []

    #total_words = 0

    #Variables que nos van a servir para los cálculos:
    raw_collection = []
    need_jump = False
    suburbs = Suburb.objects.filter(townhall=image.public_account.townhall)
    #Si tenemos varios arrays, consolidamos y construímos uno solo:
    #Esta función solo es necesaria si se recortan las imágenes manualmente
    for meta in data_subs["data"]:
        for row in meta:
            raw_collection.append(row)

    #Vamos a analizar cada una de las líneas y sus combinaciones con las líneas
    #subsecuentes:
    for idx_raw, row in enumerate(raw_collection):
        #Si la línea anterior combinó la línea actual, simplemente la ignoramos
        if need_jump:
            need_jump = False
            continue

        #Variables con sus valores default
        #Indica si es factible combinarla con la siguiente línea:
        can_be_comb = True
        #Indica qué tipo de combinación se hizo. Existen tres posibilidades:
        # curr --> con la línea actual bastaba.
        # comb --> se combinó con la línea siguiente
        # triple --> Se combinó con las siguientes dos líneas, sin embargo,
        #este tipo se calcula en otro momento, porque son muy pocas alcaldías
        #que tieenen tres lineas en el nombre y que complejiza todo.
        type_comb = None
        #Es el id de la alcaldía con la cual se encontró una coincidencia.
        sub_id = None

        #Se hará un análisis tanto de la línea actual como de la siguiente por
        # sí mismas, para analizar distintos esenarios. A la línea siguiente
        # lse llamaremos after, a la actual curr, juntas serán comb, combinando
        # las tres, se llamará triple
        try:
            after_base = raw_collection[idx_raw+1]
            comb_base = "%s %s"%(row, after_base)
        except Exception as e:
            after_base = False
        curr = get_data_suburb(row, suburbs, image)

        #Si el nombre no se puede normalizar o es válido, cancelamos la línea.
        if not curr["name"]:
            continue
        #El extrañísimo (pero siempre es posible) caso de que existan dos 
        # alcaldías distintas en el mismo lugar.
        elif curr["id"] and curr["cve"] and curr["id"] != curr["cve"]:
            set_new_error(image, "%s row: %s"%(
                u"Se encontraron dos claves en el mismo lugar", row))
            type_comb = 'error'
        #La línea tiene TOTAL sentido en sí misma:
        elif curr["id"] and curr["id"] == curr["cve"]:
            after_base = False
            type_comb = 'curr'
        #Si se pudo normalizar el texto de la siguiente línea y es válido:
        elif after_base:
            after = get_data_suburb(after_base, suburbs, image)
            comb = get_data_suburb(comb_base, suburbs, image)

            #Si lo siguiente no tiene nombre, preveer saltar
            if not after["name"]:
                need_jump = True

            if after["name"] == False:
                can_be_comb = False
                after_base = False
            #Cuando el siguiente registro tiene sentido por sí mismo:
            elif after["id"]:
                can_be_comb = False
            else:
                #Los siguientes casos asumen que hay ID actual:
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
                        set_new_error(image, "%s%s id: "%(u"Había cve sig pero" 
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
                    if idx_raw:
                        print "no puede setear el previo"
                    else:
                        pass
                try:
                    column_values[-2]["can_be_triple"] = False
                except Exception as e:
                    pass
    
        triple_base = False
        if sub_id:
            sub_id = saveFinalProjSuburb(sub_id, image, 1)
        elif after_base and can_be_comb:
            try:
                triple_text = raw_collection[idx_raw+2]
                triple_base = "%s %s"%(comb_base, triple_text)
                triple = get_data_suburb(triple_base, suburbs, image)
            except Exception as e:
                pass




        if sub_id and not type_comb:
            type_comb = 'curr'
            can_be_comb = False


        new_dict = {"seq": idx_raw,
                    "suburb_id": sub_id,
                    "image_id": image.id,
                    "type_comb": type_comb,
                    "can_be_comb": can_be_comb,
                    "curr": curr["name"],
                    "curr_raw": row,
                    "invalid": False}
        if after_base and type_comb != "error":
            new_dict["after"] = after["name"]
            new_dict["comb"] = comb["name"]
            new_dict["comb_raw"] = comb_base
        if triple_base:
            if triple["name"]:
                new_dict["triple"] = triple["name"]
                new_dict["can_be_triple"] = True

        column_values.append(new_dict)
    return column_values

def get_data_suburb(row, suburbs, image):
    if not row:
        return {"name": None, "id": None, "cve":None}
    data_dict = {}
    #El formato que devolverán: 
    #name --> nombre normalizado
    name = get_normal_name(row)
    data_dict["name"] = name
    #cve --> El id de la Colonia (Suburb) que haya coincidido si se encontró
    # una clave y si coincidió esa clave con lo que había en base de datos.
    data_dict["cve"] = get_cve(row, suburbs) if name else None
    #Id es el ID de la colonia que encontró a partir del nombre normalizado.
    data_dict["id"] = get_suburb_id(name, suburbs, image) if name else None
    return data_dict


def get_normal_name(row):
    normal_name = cleanSuburbName(row)
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

def get_cve(row, suburbs):
    cve_suburb = None
    sub_id = None
    #identificamos el formato (11-034)
    re_has_cve = re.compile(r'.*(?:\D|^)(\d{2})\s?\D?\s?(\d{3})(?:\D|$).*')
    #Se busca la clave de la colonia
    if re.match(re_has_cve, row):
        #Normalizamos el formato para aquello que "parece" clave
        cve_suburb = re.sub(re_has_cve, r'\1-\2', row)
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


def saveFinalProjSuburb(sub_id, image, simil):
    from project.models import FinalProject
    try:
        final_proy = FinalProject.objects.get(suburb__id=sub_id,
            image__isnull=True)
        final_proy.image = image
        final_proy.similar_suburb_name = simil
        final_proy.save()
        return sub_id
    except Exception as e:
        set_new_error(image, "El ID %s no lo encontramos en FinalProject"%sub_id)
        print e
        #print normal_name
        return None


def calcColumnsNumbers(data_numbers, strict=False):
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
        the_dict = calculateNumbers(rows, is_ammount, strict)
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
            #Quitamos los paréntesis que hacen ruido con (100)  y (1)
            new_value = re.sub(r'[\(\)]', '', new_value)
            #Sustituimos las Ss por 5
            new_value = re.sub(r'(s|S)', '5', new_value)
            #identificamos títulos
            if re.match(r'3\s?\/\s?1', new_value):
                print "es el título 3/1"
                continue
            #Sustituimos los diagonales por comas
            new_value = re.sub(r'(/)', ',', new_value)
            #Hacemos un conteo de letras y dígitos
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
            #números y letras, no más:
            new_value = re.sub(r'[^0-9\,\.\s\-\%\(\)]', '', new_value)
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


def calculateNumbers(rows, is_ammount, strict=False):

    re.compile(r'Variaci\wn\s[4895%]$')
    #### Variables que nos ayudarán:
    # Patrón REGEX para porcentajes válidos.
    #re_ammount = re.compile(
        #r'^(\d[\,\.](?=\d{3}))?(\d{1,3}[\,\.](?=\d{3}))?(\d{1,3})(\.\d{2})?$')
    re_ammount = re.compile( r'^\d{1,7}(\.\d{2})?$')
    re_percent = re.compile( r'^\-?\d{1,3}(\.\d{1,2})?[4895%]?\)?$')
    re_compara = re_ammount if is_ammount else re_percent
    has_percent = re.compile(r'[4895%]$')
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
            if not is_ammount and float_value > 2:
                float_value = float_value/float(100)
            new_value["final_value"] = float_value
        elif strict:
            column_values.remove(new_value)
    #print column_values
    return column_values


def set_new_error(model, text_error):
    current_notes = model.error_cell
    #print text_error
    if current_notes:
        model.error_cell = "%s\n%s"%(current_notes, text_error)
    else:
        model.error_cell = text_error
    model.save()
