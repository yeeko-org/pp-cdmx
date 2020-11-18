from scripts.exercises  import *


#extract_only_pages("AO", '0002')


execute_townhall2("AO", 'top', False, False)

execute_townhall2("AO", 'top', True, True)

#ejecutar una alcadías con reset en True
from scripts.exercises  import *
execute_townhall('BJ', False, True)


from public_account.models import PublicAccount, PPImage

public_account = PublicAccount.objects.get(id=9)
images_in_public_account = PPImage.objects\
    .filter(public_account=public_account)\
    .order_by("path")

limit_position = 'top'

self = images_in_public_account[0]
self.get_data_full_image()
self.get_table_data(limit_position=limit_position)

self.


for self in images_in_public_account:
    self.get_data_full_image()
    self.get_table_data(limit_position=limit_position)

all_ths = ["CUH", "CUJ", "TLP", "VC", "XO", "AO", "IZT", "AZC", "TLH", "MC", "MH", "COY", "GAM", "BJ", "MIL", "IZP"]


#ejecutar todas las alcadías con reset en True
execute_all_townhalls(True)

#execute_townhall(all_ths[3])

from scripts.exercises  import *
print_all_results()


#Pasar los datos por Google Lens de nueva cuenta.
lens_th('BJ')

lens_th('IZP')









from geographic.models import *
from project.models import *
from public_account.models import *


FinalProject.objects.filter(suburb__townhall__short_name="MIL", image__isnull=True).count()
FinalProject.objects.filter(suburb__townhall__short_name="MIL", image__isnull=False).count()

Suburb.object.filter()






from scripts.data_cleaner import buildSuburbComparename

buildSuburbComparename()

lst =[10,10,9,9,8]
max(set(lst), key=lst.count)




import re

re.sub(r'\(\s?(CONJ HAB|UNIDAD HABITACIONAL|U HABS)\s?\)', '(U HAB)', "KENNEDY (UNIDAD HABITACIONAL)")

ref = 'VILLA MILPA ALTA (U HAB)'
con = 'VILLA MILPA ALTA'
sin = 'FUENTES DE AZCAPOTZALCO  PARQUES DE AZCAPOTZALCO (U HAB)'

from scripts.data_cleaner import similar

similar(ref, con)
similar(ref, sin)


def input(num):
    print "ya te recibí"
    print num


def mi_preg():
    answer = input("Escribe el ID que te interesa:") 
    if answer == 1: 
        print "Hará algo con 1"
    elif answer == 2: 
        print "Hará algo con 2"
    else: 
        print("Please enter yes or no.") 


def mi_preg2():
    answer = raw_input("Enter yes or no: ") 
    if answer == "yes": 
        print "Hará algo con yes"
    elif answer == "no": 
        print "Hará algo con no"
    else: 
        print("Please enter yes or no.") 


from geographic.models import *
from project.models import FinalProject

salinas = FinalProject.objects.filter(suburb__short_name__icontains="SALINAS", 
    suburb__townhall__short_name="AZC")

specific_text = Suburb.objects.filter(name__icontains="refiere")


Suburb.objects.filter(townhall__short_name='AZC', finalproject__image__isnull=False).count()

FinalProject.objects.filter(image__isnull=False)
FinalProject.objects.filter().update(image=None)
FinalProject.objects.filter(image__isnull=False)


Suburb.objects.filter().update(compact_name=None)

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










from scripts.metodo_rules.results_ao_1 import results

for column in results["columns_data"]:
    #print len(column)
    print "--------------------"
    for col in column:
        print col["w"]



