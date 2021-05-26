# -*- coding: utf-8 -*-

import numpy

#Esta función hace una estandarización y limpieza de nombres para facilitar 
#encontrar similitudes entre los nombres oficiales y los que ponen las alcaldías

#def calculateSuburb_v3(text, maybe_cve, image):
def calculateSuburb_v3(row, final_projects):
    errors = []
    #Es el id de la alcaldía con la cual se encontró una coincidencia.
    sub_id = None

    formatted_data = row.get_formatted_data()
    normal_name = formatted_data[0]
    #cve --> El id de la Colonia (Suburb) que haya coincidido si se encontró
    # una clave y si coincidió esa clave con lo que había en base de datos.
    cve = get_cve(normal_name, final_projects, row)
    #Id es el ID de la colonia que encontró a partir del nombre normalizado.
    sub_id = get_suburb_id(normal_name, final_projects, row)

    #El extrañísimo (pero siempre es posible) caso de que existan dos 
    # alcaldías distintas en el mismo lugar.
    if sub_id and cve and sub_id != cve:
        row.set_errors("Doble coincidencia: por clave y por nombre")
        return cve, normal_name
    cve_in_proj = get_cve(formatted_data[1], final_projects, row)
    #Se devuelve la primera coincidencia:
    return cve or sub_id or cve_in_proj, normal_name

def get_cve(text, final_projects, row):
    import re
    cve_suburb = None
    sub_id = None
    #identificamos el formato (11-034)
    re_has_cve = re.compile(r'.*(?:\D|^)(\d{2})\s?\D?\s?(\d{3})(?:\D|$).*')
    #Se busca la clave de la colonia
    ### el texto puede llegar False
    if not text:
        row.set_errors(u"text Value error: %s" % text)
        return None
    if re.match(re_has_cve, text):
        #Normalizamos el formato para aquello que "parece" clave
        cve_suburb = re.sub(re_has_cve, r'\1-\2', text)
        #sabemos que el id de la alcaldía sólo llega a 16, descartamos lo que
        # sea más grande que eso
        if int(cve_suburb[:2]) < 17:
            try:
                sub_id = final_projects.get(suburb__cve_col=cve_suburb).id
            except Exception as e:
                err = "Algo que parece clave no se encontró (%s)"%cve_suburb
                row.set_errors(err)
                print 'Clave no encontrada'+cve_suburb
    return sub_id


def get_suburb_id(normal_name, final_projects, row):
    #La búsqueda se hace entre las Colonias que no han tenido coincidencias,
    # para no repetir dos registros idénticos.
    subs_found = final_projects.filter(suburb__short_name=normal_name)
    if subs_found.count() > 1:
        err = u"Varias colonias coincidentes con %s"%normal_name
        row.set_errors(err)
    if subs_found.count():
        return subs_found.first().id
    else:
        return None

#def saveFinalProjSuburb_v3(sub_id, row_data, simil=1):
def saveFinalProjSuburb_v3(sub_id, row, final_projects, simil=1):
    # from public_account.models import column_types
    from project.models import FinalProject
    try:
        final_proy = final_projects.get(suburb__id=sub_id)
    except FinalProject.DoesNotExist:
        print "No se enontró sub_id en función saveFinalProjSuburb_v3"
        return None
    row.final_proy = final_proy
    row.similar_suburb_name = simil
    # for idx, value in enumerate(row_data.get("data")):
    #     if idx:
    #         # print column_types[idx]["field"]
    #         setattr(final_proy, column_types[idx]["field"], value)
    row.save()
    return sub_id

def flexibleMatchSuburb_v3(row, sub_name, final_projects):
    from pprint import pprint
    from public_account.models import Row
    from difflib import SequenceMatcher
    # print u"----------------flexibleMatchSuburb_v3--------------------"

    max_conc = 0
    sub_id = None
    match_row_idx = -1
    max_fp = None
    for fp in final_projects:
        concordance = SequenceMatcher(None, fp.suburb.short_name,
            sub_name).ratio()
        if Row.objects.filter(final_project=fp).exists():
            concordance-= 0.001
        if concordance > 0.8 and concordance > max_conc:
            max_fp = fp
            # match_row_idx = row_idx
            match_row_idx = row.id
            max_conc = concordance
    if max_fp:
        # match_row = orphan_rows[match_row_idx]
        sub_id = saveFinalProjSuburb_v3(
            max_fp.suburb.id, row, final_projects, max_conc)


