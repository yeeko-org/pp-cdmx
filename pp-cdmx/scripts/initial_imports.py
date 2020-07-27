from project.models import * 
from geographic.models import * 
from period.models import * 



#Primero creamos todos los proyectos finales de un año determinado
def create_2018():
    all_suburbs = Suburb.objects.all()
    p_2018 = PeriodPP.objects.get(year=2018)
    for sub in all_suburbs:
        FinalProject.objects.get(period_pp=p_2018, suburb=sub)
    #comprobamos los 1812 proyectos finales:
    all_final = FinalProject.objects.all()
    print all_final.count()



#importamos los proyectos que vienen del excel:
def import_ollin_data():
    from scripts.suburbs import to_import 
    errors = [] 
    error_codes = []
    for col in to_import:
        try:
            final_proy = FinalProject.objects.get(suburb__cve_col=col['cve_col'])
            final_proy.pre_clasification = col["pre_clasification"]
            final_proy.manual_capture = col["manual_capture"]
            final_proy.save()
            #print final_proy.pre_clasification
            #print final_proy.manual_capture
        except Exception as e:
            print "%s | %s"%(col["cve_col"], col["nombre_ref"])
            errors.append(col)
            error_codes.append(e)
    print errors
    print error_codes
    print "LA SIGUIENTE COLONIA NO SE PUDO IMPORTAR:"
    col = {
        "id_ref": 1604,
        "del_ref": "TLALPAN",
        "cve_col": "12-223",
        "nombre_ref": "RESIDENCIAL FUENTES DE CANTERA (U HAB)",
        "pre_clasification": "",
        "manual_capture": "{\"approved\" : \"360176\", \"executed\" : \"360175.84\", \"progress\" : \"\"}"
    }


def set_posb_2010(test):
    example_pob=[{
        "id_ref": 1,
        "del_ref": "ALVARO OBREGON",
        "cve_col": "10-241",
        "nombre_ref": "19 DE MAYO",
        "pob_2010": 1347
    }]
    test = False
    from scripts.pobs import all_cols 
    errors = [] 
    error_codes = []
    colst_to_insert = example_pob if test else all_cols
    for col in colst_to_insert:
        try:
            current_sub = Suburb.objects.get(cve_col=col['cve_col'])
            current_sub.pob_2010 = col["pob_2010"]
            current_sub.save()
            #print final_proy.pre_clasification
            #print final_proy.manual_capture
        except Exception as e:
            print "%s | %s | %s"%(col["cve_col"], col["nombre_ref"], col["del_ref"])
            errors.append(col)
            error_codes.append(e)
    print errors
    print error_codes


def sin_pob_2010():
    subs_sin_pob = Suburb.objects.filter(pob_2010__isnull=True)
    print subs_sin_pob.count()
    for sub in subs_sin_pob:
        print "%s | %s | %s"%(sub.cve_col, sub.name, sub.townhall.name)





