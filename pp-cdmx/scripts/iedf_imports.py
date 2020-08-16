# -*- coding: utf-8 -*-
from project.models import *
from geographic.models import *
from period.models import *


def calculate_stats():
    errors = []
    error_codes = []

    all_proyects = FinalProject.objects.all()

    for col in all_proyects:
        try:
            final_proy = FinalProject.objects.get(
                suburb__cve_col=col['cve_col'])
            proys = None
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
    from django.db.models import Max, Sum
    from classification.models import Anomaly

    subs_sin_pob = Suburb.objects.filter(pob_2010__isnull=True)

    # print subs_sin_pob.count()
    # for sub in subs_sin_pob:
    #     print "%s | %s | %s" % (sub.cve_col, sub.name, sub.townhall.name)

    for suburb in Suburb.objects.all():
        project_suburb_year_query = Project.objects\
            .filter(suburb=suburb, period_pp__year=year)
        votes__max = project_suburb_year_query\
            .aggregate(Max('votes')).get("votes__max")
        votes__sum = project_suburb_year_query\
            .aggregate(Sum('votes')).get("votes__sum")

        final_project = FinalProject.objects\
            .filter(suburb=suburb, period_pp__year=year).first()

        final_project.total_votes = votes__sum
        final_project.save()

        if votes__max:
            winer_proyects = project_suburb_year_query\
                .filter(votes=votes__max)
            count_winers = winer_proyects.count()
            winer_proyects.update(is_winer=True)
            if count_winers > 1:
                anomaly, is_created = Anomaly.objects\
                    .get_or_create(name=u"Empate de votos")
                anomaly_fp, is_created = AnomalyFinalProject.objects\
                    .get_or_create(
                        anomaly=anomaly,
                        final_project=final_project)
        else:
            # sin proyecto ganador
            count_winers = 0

        print "%s | %s | %s" % (
            suburb.cve_col, suburb.name, suburb.townhall.name)
        print "votes__max: %s" % votes__max
        print "votes__sum: %s" % votes__sum
        print "final_project: %s" % final_project
        print "winer_proyects: %s" % winer_proyects
        print "count_winers: %s" % count_winers
        print

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

