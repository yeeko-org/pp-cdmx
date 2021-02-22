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




############### NUEVOS EJERCICIOS FEBRERO 2021 ######################


from public_account.models import PublicAccount, PPImage
from pprint import pprint
import json


PPImage.objects.filter(need_manual_ref=True).update(need_second_manual_ref=True)

img_pev=None
for image in PPImage.objects.filter(need_manual_ref=True,
    manual_ref__isnull=False).exclude(id=129):
    if img_pev:
        img_pev.manual_ref=image.manual_ref
    img_pev=image
    image.save()


from public_account.models import PublicAccount, PPImage
from pprint import pprint
import json
img_prev=None
for image in PPImage.objects.filter(need_manual_ref=True, 
    manual_ref__isnull=False).exclude(id=129):
    if img_prev:
        img_prev.manual_ref=image.manual_ref
        img_prev.save()
    img_prev=image




from public_account.models import PublicAccount, PPImage
#public_accounts=PublicAccount.objects.filter(id__in=[93, 25, 95])
public_accounts=PublicAccount.objects.filter(id__in=[46])
for pa in public_accounts:
  pa.column_formatter_v2(True)


from project.models import FinalProject
from public_account.models import PublicAccount, PPImage

#for pa in PublicAccount.objects.all():
for pa in PublicAccount.objects.filter(id__in=[46]):
    sum_complete = 0
    print "    ----------->   %s - %s   <----------"%(pa.period_pp, pa.townhall)
    for image in PPImage.objects.filter(public_account=pa):
        complete = FinalProject.objects.filter(image=image).count()
        sum_complete+=complete
        if not complete:
            print image.path
    ths = FinalProject.objects.filter(period_pp=pa.period_pp,
      suburb__townhall=pa.townhall).count()
    #print "%s / %s"%(sum_complete, ths)
    print round(sum_complete/float(ths) * 100 , 1)




from project.models import AnomalyFinalProject, FinalProject
from public_account.models import PublicAccount
from classification.models import Anomaly

AnomalyFinalProject.objects.all().count()


pa_with_anoms = PublicAccount.objects.filter(anomalyfinalproject__isnull=False)



#Eliminaré todas las anomalías asociadas a un proyecto

all_fp_anoms = AnomalyFinalProject.objects\
    .filter(final_project__isnull=False, anomaly__is_public=False)\
    .exclude(anomaly__name__icontains="IECM")

filter_fp_anoms = AnomalyFinalProject.objects\
    .filter(final_project__isnull=False, anomaly__is_public=False)\
    .exclude(anomaly__name__icontains="IECM")\
    .exclude(anomaly__name__icontains="Vari")

all_fp_anoms.count()
#21170

#para borrar las asociaciones previas
all_fp_anoms.delete()

fp_with_anoms = FinalProject.objects\
    .filter(anomalyfinalproject__in=all_fp_anoms)

print fp_with_anoms.distinct().count()

fp_with_normal_anoms = FinalProject.objects\
    .filter(anomalyfinalproject__in=filter_fp_anoms)

print fp_with_normal_anoms.distinct().count()




#Comprobación de las anomalías a borrar
anoms = Anomaly.objects.filter(anomalyfinalproject__in=all_fp_anoms).distinct()
print anoms

for anom in anoms:
    print anom
    print all_fp_anoms.filter(anomaly=anom).count()



#Recalcular las anomalías:


all_fp = FinalProject.objects.filter(data_raw__isnull=False)

for fp in all_fp:
    data_raw = fp.get_data_raw()
    try:
        errors = data_raw["errors"]
    except Exception as e:
        continue
    for error in errors:
        anomaly, created = Anomaly.objects\
            .get_or_create(name=error, is_public=False)
        afp, crt2 = AnomalyFinalProject.objects.get_or_create(
            final_project=fp, anomaly=anomaly)


fp_with_var = FinalProject.objects.filter(variation__isnull=False).values("variation")

list_var2 = fp_with_var.distinct()
list_var3 = list(list_var2)

newlist = sorted(list_var3, key=lambda x: x["variation"], reverse=True)

for fp in newlist:
    print fp["variation"]

list_var = list(fp_with_var)

len(list_var)




from project.models import FinalProject

>>> FinalProject.objects.filter(image__isnull=False).count()
10001
>>> FinalProject.objects.filter(image__isnull=True).count()
871



from public_account.models import PPImage, PublicAccount

for public_account in PublicAccount.objects.all():
    public_account.column_formatter_v2(True)

special_pa = PublicAccount.objects.get(id=82)
special_pa.column_formatter_v2(True)

>>> FinalProject.objects.filter(image__isnull=False).count()
10029
>>> FinalProject.objects.filter(image__isnull=True).count()
843



PPImage.objects.filter(manual_ref__isnull=False).count()

Casos sin resolver:


No confiar en las claves de la siguiente cuenta pública:
----Cuenta publica 2017 -- IZP, id: 82----

Todo mal con table_data:
2014 -- AO PP-2014-AO_0003.png 876

2016 -- AZC PP-2016-AZC_0003.png 548
2016 -- AZC PP-2016-AZC_0004.png 549
2016 -- AZC PP-2016-AZC_0005.png 550
2016 -- AZC PP-2016-AZC_0006.png 551
2016 -- AZC PP-2016-AZC_0007.png 552
2016 -- AZC PP-2016-AZC_0008.png 553
2016 -- AZC PP-2016-AZC_0009.png 554
2016 -- AZC PP-2016-AZC_0010.png 555
2016 -- AZC PP-2016-AZC_0011.png 556


2016 -- XO PP-2016-XO_0004.png 738


    2015 -- GAM PP-2015-GAM_0002.png 781
error al convertir en calculateNumber: "407,510.00  100.0 %"
invalid literal for float(): 407.510.00100.0
error al convertir en calculateNumber: "407,510.00  100.0 %"
invalid literal for float(): 407.510.00100.0


    2016 -- BJ PP-2016-BJ_0005.png 561
error al convertir en calculateNumber: "100.0  100.0"
invalid literal for float(): 100.0100.0

----Cuenta publica 2016 -- COY, id: 54----
    2016 -- COY PP-2016-COY_0001.png 567
error al convertir en calculateNumber: "99.70  99.70"
invalid literal for float(): 99.7099.70
error al convertir en calculateNumber: "95.98 99.70  99.98"
invalid literal for float(): 95.9899.7099.9
    2016 -- COY PP-2016-COY_0002.png 568
error al convertir en calculateNumber: "99.98  99.98"
invalid literal for float(): 99.9899.9
    2016 -- COY PP-2016-COY_0003.png 569
error al convertir en calculateNumber: "100.00  100.00"
invalid literal for float(): 100.00100.00
error al convertir en calculateNumber: "99,94 99.98  99.94"
invalid literal for float(): 99.9499.9899.9
    2016 -- COY PP-2016-COY_0004.png 570
error al convertir en calculateNumber: "97.62 99.88 99.40 200.00  97.62"
invalid literal for float(): 97.6299.8899.40200.0097.62
    2016 -- COY PP-2016-COY_0005.png 571
error al convertir en calculateNumber: "100.00  100.00"
invalid literal for float(): 100.00100.00
    2016 -- COY PP-2016-COY_0006.png 572
error al convertir en calculateNumber: "200.00  100.00"
invalid literal for float(): 200.00100.00
error al convertir en calculateNumber: "200.00  100.00"
invalid literal for float(): 200.00100.00
error al convertir en calculateNumber: "100.00  100.00"
invalid literal for float(): 100.00100.00
    2016 -- COY PP-2016-COY_0007.png 573
error al convertir en calculateNumber: "9.36  99.36"
invalid literal for float(): 9.3699.36
error al convertir en calculateNumber: "99.86  99.86"
invalid literal for float(): 99.8699.86


    2019 -- AZC PP-2019-AZC_0006.png 395
error al convertir en calculateNumber: "100 %  100 %"


    2019 -- XO PP-2019-XO_0003.png 533
error al convertir en calculateNumber: "100 %  10000 %"
invalid literal for float(): 100%10000