# -*- coding: utf-8 -*-
from geographic.models import Suburb

# from period.models import (LawPP, PeriodPP, result_percent, print_results)

from project.models import (
    FinalProject,
    # check_names, key_similar_value, find_winner,
)


def calculate_stats():
    subs_sin_pob = Suburb.objects.filter(pob_2010__isnull=True)
    errors = []
    error_codes = []

    all_proyects = FinalProject.objects.all()

    for col in all_proyects:
        try:
            final_proy = FinalProject.objects.get(
                suburb__cve_col=col['cve_col'])
            # proys = None
            final_proy
        except Exception as e:
            print "%s | %s" % (col["cve_col"], col["nombre_ref"])
            errors.append(col)
            error_codes.append(e)
    print errors
    print error_codes

    print subs_sin_pob.count()
    for sub in subs_sin_pob:
        print "%s | %s | %s" % (sub.cve_col, sub.name, sub.townhall.name)


def calculate_winner(year=2018):
    for final_project in FinalProject.objects.filter(period_pp__year=year):
        final_project.calculate_winner()


def CategoriesIECM20180():
    from classification.models import CategoryIECM
    names = [["Actividades culturales", "fa-palette"],
             ["Actividades recreativas", "fa-kite"],
             ["Actividades deportivas", "fa-running"],
             ["Obras y servicios", "fa-hard-hat"],
             ["Prevención del delito", "fa-bell"],
             ["Infraestructura urbana", "fa-city"],
             ["Equipamiento", "fa-tree"]]
    for name in names:
        cat = CategoryIECM.objects.get(name=name[0])
        cat.icon = name[1]
        cat.save()
