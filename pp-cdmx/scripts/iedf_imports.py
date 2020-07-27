from project.models import * 
from geographic.models import * 
from period.models import * 


# -*- coding: utf-8 -*-
def calculate_stats():



errors = [] 
error_codes = []

all_proyects = FinalProject.objects.all()

for col in all_proyects:
    try:
        final_proy = FinalProject.objects.get(suburb__cve_col=col['cve_col'])
        proys = 
        final_proy 
    except Exception as e:
        print "%s | %s"%(col["cve_col"], col["nombre_ref"])
        errors.append(col)
        error_codes.append(e)
print errors
print error_codes

print subs_sin_pob.count()
for sub in subs_sin_pob:
    print "%s | %s | %s"%(sub.cve_col, sub.name, sub.townhall.name)


def calculate_winner():
    subs_sin_pob = Suburb.objects.filter(pob_2010__isnull=True)
    print subs_sin_pob.count()
    for sub in subs_sin_pob:
        print "%s | %s | %s"%(sub.cve_col, sub.name, sub.townhall.name)


