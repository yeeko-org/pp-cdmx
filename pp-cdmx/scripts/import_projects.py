​# -*- coding: utf-8 -*-
from project.models import Project
from geographic.models import Suburb
from period.models import PeriodPP
from classification.models import CategoryIECM
import csv

from project_data import project_data  

for data in project_data:
    period_pp_year = data.get("period_pp_year")
    suburb_cve_col = data.get("suburb_cve_col")
    project_id = data.get("project_id") or None
    category_iecm_name = data.get("category_iecm_name")
    name_iecm = data.get("name_iecm")
    votes_mro = data.get("votes_mro") or "0"
    votes_int = data.get("votes_int") or "0"
    votes = data.get("votes") or "0"
    suburb = Suburb.objects.filter(cve_col=suburb_cve_col).first()
    try:
        period_pp = PeriodPP.objects.get(year=int(period_pp_year))
    except Exception as e:
        print e
        continue
    if not suburb:
        #print error
        print "Suburb no contrado:"
        print suburb_cve_col
        continue
    if category_iecm_name:
        category_iecm, is_created = CategoryIECM.objects.get_or_create(
            name=category_iecm_name
            )
    else:
        category_iecm_name=None
    project, is_created=Project.objects.get_or_create(
        suburb=suburb,
        period_pp=period_pp,
        name_iecm=name_iecm,
        project_id=project_id
        )
    project.category_iecm = category_iecm
    project.votes_mro = int(votes_mro.replace(",", ""))
    project.votes_int = int(votes_int.replace(",", ""))
    project.votes = int(votes.replace(",", ""))
    project.save()
    #print project
