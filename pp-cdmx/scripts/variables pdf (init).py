# -*- coding: utf-8 -*-
from vision.get_columns import extractDataForLens

path = u'G:\\Mi unidad\\YEEKO\\Clientes\\Ollin-Presupuesto participativo\\Bases de datos\\Cuenta Pública\\init\\p'

from vision.get_columns import extractDataForLens

from public_account.models import PPImage, PublicAccount
from project.models import FinalProject

FinalProject.objects.all().update(image=None)
x=PPImage.objects.all().first()
#y,z=x.calcColumnsNumbers()
a=x.calculateSuburb()
from pprint import pprint
pprint(a)







import re
from geographic.models import *

import unidecode
from public_account.models import *
from period.models import *
import numpy
from vision.get_columns import get_year_data
import json

dels = ["CUH", "CUJ", "TLP", "VC", "XO", "AO", "IZT", "AZC", "TLH", "MC", "MH", "COY", "GAM", "BJ", "MIL"]

path_image = u'G:\\Mi unidad\\YEEKO\\Clientes\\Ollin-Presupuesto participativo\\Bases de datos\\Cuenta Pública\\init\\p'


data_from_lens = get_year_data(path_image, 2018, dels[0])


data_for_tests = data_from_lens[dels[0]]


##$env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\rick_\keys\googlelens.json"

from vision.get_columns import extractDataForLens
path = u'G:\\Mi unidad\\YEEKO\\Clientes\\Ollin-Presupuesto participativo\\Bases de datos\\Cuenta Pública\\init\\p'
curr_th = "AZC"
extractDataForLens(path, th=curr_th)



#Continuación de la función que ya te pedí en PublicAccount:

#Lucian, creo que ya no es necesario importar esto:
from public_account.models import PPImage, PublicAccount

pa = PublicAccount.filter(suburb__shortname=curr_th)
column_formatter(pa)

#LUCIAN, en realidad hay que cambiar los pa por self
#def la_funcion_que_agregaste(self):
def column_formatter(self):
    #LUCIAN: Esto es solo la continuación de lo que ya comenzaste
    #Lucian, creo que ya no es necesario importar esto:
    from public_account.models import PPImage, PublicAccount
    is_pa_stable = True
    all_images = PPImage.objects.filter(public_account=self)
    all_orphan_rows: {"suburbs":[], "numbers":[]}
    for image in all_images:
        ord_suburbs= image.calculateSuburb()  
        number_results, len_array = image.calcColumnsNumbers()
        import numpy
        standar_dev = numpy.std(len_array)
        is_stable = standar_dev < 1
        if is_stable:
            rows_count = int(round(numpy.mean(len_array)))
            #LUCIAN: Hay que agregar "rows_count" al modelo
            #x.rows_count = rows_count
            #x.save()
            ord_numbers = []
            amm_types= ["progress", "approved", "modified", "executed", "variation"]
            for idx, row in enumerate(xrange(rows_count)):
                complete_row = {}
                is_valid = False
                for idx_amm,ammount in enumerate(amm_types):
                    try:
                        complete_row[ammount] = number_results[idx_amm][idx]
                    except Exception as e:
                        print e
                complete_row["seq"] = idx
                ##RICK: -->
                complete_row["image_id"] = image.id
                ##<----
                ord_numbers.append(complete_row)
            all_orphan_rows = comprobate_stability(all_orphan_rows, 
                                    ord_numbers, ord_suburbs, image)
        else:
            print "inestable_numbers"
            #LUCIAN: Falta el siguiente campo en el modelo:
            #image.status = "inestable_numbers"
            #image.save()
            is_pa_stable = False
            continue
    if is_pa_stable:
        #si existen filas huérfanos:
        len_orphan = len(all_orphan_rows)
        new_orphan_rows = []
        if len_orphan:
            print "haremos un match suavizado"
            orphan_subs = all_orphan_rows["suburbs"]
            all_orphan_rows["suburbs"] = flexibleMatchSuburb(orphan_subs, self)
            new_orphan_rows = formatter_orphan(all_images, all_orphan_rows)
            len_new_orphan = len(new_orphan_rows)
        if not len_orphan or not len_new_orphan:
            self.status = "completed"
            self.save()
            return
        else:
            print "hubo algunos datos que no logramos insertar"
            print new_orphan_rows
            self.status = "incompleted"
            self.save()
            return
    if not is_pa_stable:
        self.status = "inestable_images"
        self.save()


def formatter_orphan(all_images, all_orphan_rows):
    new_orphan_rows = {"suburbs":[], "numbers":[]}
    for image in all_images:
        current_suburbs = [x for x in all_orphan_rows["suburbs"] if x["image_id"] == image.id]
        current_numbers = [x for x in all_orphan_rows["numbers"] if x["image_id"] == image.id]
        #signfica que no coincidieron las columnas de ambos recortes:
        if len(current_numbers):
            new_orphan_rows = comprobate_stability(new_orphan_rows, 
                                    current_numbers, current_suburbs, image)
        else:
            orphan_stable_subs = save_complete_rows(image, current_numbers,
                                                             current_suburbs)
            new_orphan_rows["suburbs"].append(orphan_stable_subs)
    return new_orphan_rows





def comprobate_stability(all_orphan_rows, ord_numbers, ord_suburbs, image):
    stable_row = len(ord_numbers) == len(ord_suburbs)
    if not stable_row:
        real_ord_suburbs = [x for x in ord_suburbs if x["suburb_id"]]
        if len(ord_numbers) == len(real_ord_suburbs):
            stable_row = True
            ord_suburbs = real_ord_suburbs
    #el número de columnas coincide:
    if stable_row:
        orphan_stable_subs = save_complete_rows(image, ord_numbers, ord_suburbs)
        all_orphan_rows["suburbs"].append(orphan_stable_subs)
    else:
        print "inestable_suburbs"
        all_orphan_rows["numbers"].append(number_results)
        all_orphan_rows["suburbs"].append(ord_suburbs)
        #LUCIAN: Falta el siguiente campo en el modelo:
        #image.status = "inestable_suburbs"
        #image.save()
    return all_orphan_rows



def save_complete_rows(image, ordered_numbers, ordered_suburbs):
    from pprint import pprint
    #LUCIAN: checa esta función, existe?
    from scripts.common import get_or_none
    from project.models import FinalProject
    #LUCIAN: Estoy imprimiendo esto para ayudar a las pruebas
    pprint(ordered_numbers)
    pprint(ordered_suburbs)
    #aquí vas a tomar, en el orden en el que están y los vas a insertar
    is_complete = True
    orphan_rows=[]
    for idx, column_num in ennumerate(ordered_numbers):
        sub = ordered_suburbs[idx]
        suburb_id = sub.suburb_id
        if suburb_id:
            #LUCIAN, estoy harcodeando 2018, ¿de dónde debe salir?
            final_proj = FinalProject.objects.get_or_none(
                suburb__id=suburb_id, period_pp=2018)
            if final_proj:
                final_proj.approved = column_num.approved
                final_proj.modified = column_num.modified
                final_proj.executed = column_num.executed
                final_proj.progress = column_num.progress
                #LUCIAN: el siguiente campo todavía no existe en la base de datos, agrégalo
                #final_proj.variation = column_num.variation
                final_proj.image=x
                final_proj.save()
        if not final_proj:
            ##RICK---> Estoy hay que evitarlo la segunda vez
            sub["number_data"] = column_num
            ##<----
            orphan_rows.append(sub)
            is_complete=False
            continue
    if is_complete:
        #LUCIAN: La siguiente variable no existe en el modelo, hay que agregarla:
        #image.status = "completed"
        #image.save()
        print "completed"
    else:
        #LUCIAN: falta campo
        #image.status = "stable_row"
        print "Hay cosas que faltan por completar"
    return orphan_rows



#def flexibleMatchSuburb(townhall_data):
def flexibleMatchSuburb(orphan_subs, pa):
    from geographic.models import Suburb
    missing_row_idxs = [idx for idx, x in enumerate(orphan_subs) if not x["suburb_id"]]
    miss_subs = Suburb.objects.filter(townhall=pa.townhall,
                finalproject__period_pp__year=pa.period_pp,
                finalproject__image__isnull=True)
    for sub in missings_subs:
        max_conc = 0
        final_row_idx = -1
        for row_idx in missing_row_idxs:
            concordance = similar(sub.short_name, 
                orphan_subs[row_idx]["raw_normalized"])
            if concordance > 0.8 and concordance > max_conc:
                final_row_idx = row_idx
                max_conc = concordance 
        if final_row_idx > -1:
            orphan_subs[final_row_idx]["suburb_id"] = sub.id
            orphan_subs[final_row_idx]["concordance"] = max_conc
            print "-------------"
            print sub.short_name
            #print orphan_subs[final_row_idx]["raw_normalized"]
            print orphan_subs[final_row_idx]
    return orphan_subs





    miss_subs, miss_rows = calculateMissings(all_rows, th)

    for sub in miss_subs:
        print sub.short_name

    for row_idx in miss_rows:
        print all_rows[row_idx]["raw_normalized"]
        print all_rows[row_idx]["suburb_id"]


print ids_included
print "Total:"
print subs_count
print "completos:"
print len(subs_with_match)






def foundAllMatches():


    for idx in [0]:

    idx = 0
    all_rows = import_json(all_pages[idx])

    #subs_count = Suburb.objects.filter(
        #townhall__short_name=th).count()



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




