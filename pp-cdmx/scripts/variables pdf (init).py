# -*- coding: utf-8 -*-
import re
from geographic.models import *
from difflib import SequenceMatcher
import unidecode
from public_account.models import *
from period.models import *
import numpy

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
    final_name = re.sub(r'\(\s?(.*)(\S+)\s?\)', '(\\1\\2)', final_name)
    #compact_name = re.sub(r'[^0-9A-Z]', '', final_name)
    return final_name

def buildSuburbComparename():
    all_suburbs = Suburb.objects.all()
    for sub in all_suburbs:
        sub.short_name=cleanSuburbName(sub.name)
        sub.save()


from scripts.first_scraping import all_pages

def import_json(curr_pages):
    suburbs_dict = []
    th = TownHall.objects.get(short_name=curr_pages["townhall"]) 
    period = PeriodPP.objects.get(year=curr_pages["period"]) 
    pa, created = PublicAccount.objects.get_or_create(period_pp=period, 
        townhall=th)
    pages_dict =  dict.items(curr_pages["images"])
    #return pages_dict
    for page in pages_dict:
        image, created = PPImage.objects.get_org_create(
            public_account=pa, path=page[0])
        data_numbers = page[1]["2"]
        number_results, len_array = calcColumnsNumbers(data_numbers, th)
        is_stable = numpy.std(len_array) < 1
        if is_stable:
            ordered_numbers = []
            for column in number_results:
                ordered_numbers.append()
            number_of_rows = round(numpy.mean(len_array))
            amm_types= ["avance", "approved", "modified", "executed", "progress"]
            for idx, row in ennumerate(xrange(number_of_rows)):
                complete_row = {}
                for idx_amm,ammount in ennumerate(amm_types):
                    try:
                        complete_row[ammount] = number_results[idx_amm][idx]
                    except Exception as e:
                        raise e
                ordered_numbers.append(complete_row)
        print page[0]
        print "--------"
        data_subs = page[1]["1"]
        page_result = calculateSuburb(data_subs, th, image)
        #print page_result
        suburbs_dict+=page_result
        #return number_results
    return suburbs_dict


idx = 0
all_rows = import_json(all_pages[idx])


for row in all_rows:
    print "------------"
    for r in row:
        print r



def calculateSuburb(data_subs, th, image):
    column_values = []
    #Antes que nada, validamos que sea una columna válida:
    #total_words = 0
    suburbs = Suburb.objects.filter(townhall=th)
    seq = 0 
    for meta in data_subs["data"]:
        for rows in meta:
            seq+=1
            the_dict = matchSuburb(rows, suburbs, seq, image)
            if the_dict:
                column_values.append(the_dict)
    return column_values


def calcColumnsNumbers(data_numbers, th_short):
    column_values = []
    large_row = 0
    seq = 0
    column_number = 1 
    current_len = 0
    len_array = []
    for rows in data_numbers["data"]:
        is_ammount = (column_number > 1 and column_number < 5)
        seq+=1
        the_dict = calculateNumbers(rows, is_ammount, seq)
        if the_dict:
            len_dict = len(the_dict)
            large_row = large_row or len_dict
            current_len+=len_dict
            if current_len +2  >= large_row:
                column_number+=1
                column_values.append(the_dict)
                print current_len
                len_array.append(current_len)
                current_len = 0
            else:
                column_values[-1]+=the_dict
            #column_values[column_number-1]=the_dict
    return column_values, len_array


def calculateNumbers(rows, is_ammount, seq):
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
        raw_non_spaces = len(re.sub(r'[^\S]', '', new_value))
        #Sustituimos las Bs por 8
        new_value = re.sub(r'(B)', '8', new_value)
        #Sustituimos las Os por 0
        new_value = re.sub(r'(O)', '0', new_value)
        new_value = re.sub(r'(/)', ',', new_value)
        #Nos quedamos solo con lo que utilizaremos
        new_value = re.sub(r'[^0-9\,\.\s\-\%\(\)]', '', new_value)
        clean_non_spaces = len(re.sub(r'[^\S]', '', new_value))
        
        #La mayor parte que sean los números
        try:
            if (clean_non_spaces / float(raw_non_spaces)) < 0.8:
                print "casi todos son letras"
                continue
        except Exception as e:
            print e
            continue
        #Limpieza básica de espacios:
        new_value = new_value.strip()
        
        #Se quitan los espacios alrededor de puntos y comas (siempre a puntos) ||  4 , 5 --> 4,5
        new_value = re.sub(r'(\d)\s?[\.,]\s?(\d)', '\\1.\\2', new_value)
        
        if not is_ammount:
            #Se quita el espacio entre el número y el porcentaje, en caso de existir.
            new_value = re.sub(r'(\d)\s?%', '\\1%', new_value)
            #Se quitan los espacios después del abrir paréntesis y antes de cerrarlos
            new_value = re.sub(r'\(\s?(.+)\s?\)', '\\1', new_value)
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
            new_value["final_value"] = float(only_ints)
    
    #print column_values
    return column_values



def matchSuburb(row, suburbs, seq, image, period=2018):
    #identificamos el format (11-034)
    re_has_cve = re.compile(r'^.*(\d{2})\-(\d{3})(?:\D|$).*')
    normal_name = cleanSuburbName(row)
    raw_non_spaces = len(re.sub(r'[^\S]', '', normal_name))
    #print normal_name
    
    #Validadores para excluir palabras que ya conocemos
    if bool(re.search(
        r'(COLONIA O PUEBLO|PUEBLO ORIGINARIO|UNIDAD RESPON)', normal_name)):
        return False
        #continue
    #Esto significa que llegamos al final
    elif bool(re.search(r'(SE REFIERE EL|REMANENTE|TOTAL|AUTORIZADO|ELABORO)', normal_name)):
        return False
        #break
    #En el caso de que se coma letras de otra columna
    elif raw_non_spaces < 4:
        return False
        #continue
    
    new_dict = {"suburb_id": None}
    #Se busca la clave de la colonia
    the_sub = False
    if (bool(re.search(re_has_cve, row))):
        cve_subur = re.sub(re_has_cve, '\\1-\\2', row)
        print cve_subur
        if int(cve_subur[:2]) < 17:
            try:
                the_sub = suburbs.get(cve_col=cve_subur)
            except Exception as e:
                print 'No encontrado'
    if not the_sub:
        subs_found = suburbs.filter(short_name=normal_name,
            finalproject__period_pp__year=period,
            finalproject__image__isnull=True)
        if subs_found.count() > 1:
            print "varios"
            print subs_found
        elif subs_found.count()  == 1:
            the_sub = subs_found[0]
        else:
            print normal_name
    if the_sub:
        try:
            final_proy = FinalProject.objects.get(suburb__id=the_sub.id,
                image__isnull=True)
            final_proy.image = image
            final_proy.save()
            new_dict["suburb_id"] = the_sub.id
        except Exception as e:
            print e
    new_dict["raw_origin"] = row
    new_dict["raw_normalized"] = normal_name
    new_dict["seq"] = seq
    return new_dict




def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()



def foundAllMatches():


for idx in [0]:

idx = 0
all_rows = import_json(all_pages[idx])

#subs_count = Suburb.objects.filter(
    #townhall__short_name=th).count()



def calculateMissings(all_rows, th):
    subs_with_match = [x for x in all_rows if x["suburb_id"]]
    ids_included = [x["suburb_id"] for x in subs_with_match]
    missings_subs = Suburb.objects.filter(
        townhall__short_name=th).exclude(id__in=ids_included)
    missing_rows = [idx for idx, x in enumerate(all_rows) if not x["suburb_id"]]
    print len(missing_rows)
    print len(missings_subs)
    return missings_subs, missing_rows


hidalgo = []
for x in all_rows:
    if "ESTADO" in x["raw_normalized"]:
        hidalgo.append(x)


missings_subs, missing_rows = calculateMissings(all_rows, th)


for sub in missings_subs:
    max_conc = 0
    final_row_idx = -1
    for row_idx in missing_rows:
        concordance = similar(sub.short_name, 
            all_rows[row_idx]["raw_normalized"])
        if concordance > 0.8 and concordance > max_conc:
            final_row_idx = row_idx
            max_conc = concordance 
    if final_row_idx > -1:
        all_rows[final_row_idx]["suburb_id"] = sub.id
        all_rows[final_row_idx]["concordance"] = max_conc
        print "-------------"
        print sub.short_name
        #print all_rows[final_row_idx]["raw_normalized"]
        print all_rows[final_row_idx]


missings_subs, missing_rows = calculateMissings(all_rows, th)

for sub in missings_subs:
    print sub.short_name

for row_idx in missing_rows:
    print all_rows[row_idx]["raw_normalized"]
    print all_rows[row_idx]["suburb_id"]





print ids_included
print "Total:"
print subs_count
print "completos:"
print len(subs_with_match)


foundAllMatches()

print to_dict


[x for x in myList if x.n == 30]  # list of all elements with .n==30




#PRUEBAS EXITOSAS:
"""
percents = ['12.38' , '21. 29', '-2.678', '-3 . 29', '-3 . 29 -4 . 98',  '1018',  '101 %',  '1018', '1011', 'recibe:']

percents2 = ['12.3' , '21.2', '-2.67', '-3.2']

is_ammount = False
calculateNumbers(percents, is_ammount)


data = ["100.00", "100.00", "99.98 0.00", "99.27", "99.16", "0.00", "99.27", "0.00", "99.42", "99.27", "99.68", "99.16", "99.27", "99.16", "99.27", "99.27", "99.94", "99.84", "100.00"]

ammounts = ["Aprobado 1", "439,815.40", "439,815.40", "439,815.40", "439 , 815.40", "439,815.40", "439,815.40", "439 , 815.40", "439 , 815.40", "439 , 815.40", "439,815.40", "439,815.40", "439,815.40", "439,815.40", "439 , 815.40", "439 , 815.40", "439 , 815.40", "439 , 815.40", "439,815.40", "439,815.40", "439 , 815.40", "439,815.00", "48,819,509.00"]

calculateNumbers(ammounts)
"""






palabras / frases



#Antes que nada, construir función que estandarice los textos, que incluya:
#GUARDADO DE BASE DE DATOS.
#--Espacios + paréntesis. || ( EJEMPLO ) --> (EJEMPLO)
#--Espacios y puntos.  || EJEMPLO . INCREIBLE --> EJEMPLO. INCREIBLE
#--Espacios y comas. || EJEMPLO , INCREIBLE --> EJEMPLO, INCREIBLE
#--Dobles espacios.
#--Para los montos, eliminar las comas. || 482,
#Además, estandarizar con los siguientes criterios
#PARA COMPARAR. (usar slugify)
#--Acentos --> frases sin un solo acento || ÁRBOL --> ARBOL
#--Todo Mayúsculas  
#--comas --> espacios
#--puntos --> espacios
#--ignorar todo lo que no sea espacio o [a-Z, 0-9, ()]
#considerar los siguientes casos:
# SANTA FE (PBLO), SANTA FE (U HAB)
#(U HAB) (U.HAB.) (U. HAB.) --> (U HAB)
