# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class PublicAccountMatchMix:

    def calculate_match_v3(self, reset=False, image_num=None):
        from project.models import FinalProject
        # from public_account.models import PPImage, Row
        from public_account.models import Row
        print
        print
        print "----Cuenta publica %s, id: %s----" % (self, self.id)
        # import numpy
        # suburbs_dict = []

        # all_images = PPImage.objects.filter(public_account=self)
        # if image_num:
        #     all_images = all_images.filter(path__icontains=image_num)

        # all_images = all_images.order_by("path")

        final_projects = FinalProject.objects\
            .filter(suburb__townhall=self.townhall, period_pp=self.period_pp)

        """
        Una vez obtenido los valores de special_formats, se tratan los datos:
        """
        # Intentamos obtener los datos que nos interesan
        # print image.path
        # Por cada fila de datos:
        all_rows = Row.objects.filter(
            image__public_account=self,
            formatted_data__isnull=False)\
            .exclude(formatted_data="[]")

        for row in all_rows:
            # errors = row.get_errors()
            # Intentamos obtener de forma simple el id de la colonia.
            sub_id, normal_name = calculateSuburb_v3(row, final_projects)

            # row_data = []

            new_sub_id = None
            if sub_id:
                new_sub_id = saveFinalProjSuburb_v3(
                    sub_id, row, final_projects)
                # sub_id, all_row)
            if not new_sub_id:
                print "no hay new_sub_id: ", normal_name

        # all_orphan_rows = self.get_orphan_rows()
        all_orphan_rows = all_rows.filter(final_project__isnull=True)
        # ###limitado solo a los row de la cuenta publica?
        print "total rows: ", all_rows.count()
        print u"coincidencia exacta: ", all_rows.filter(
            final_project__isnull=False).count()

        for orphan_row in all_orphan_rows:
            formatted_data = row.get_formatted_data()
            if formatted_data:
                print "----------------"
                print formatted_data[0]
                # orphan_fps = final_projects.filter(row__isnull=True)
                flexibleMatchSuburb_v3(row, formatted_data[0], final_projects)
        print u"total coincidencias: ", all_rows.filter(
            final_project__isnull=False).count()

        return


# Esta función hace una estandarización y limpieza de nombres para facilitar
# encontrar similitudes entre los nombres oficiales y los que ponen las
# alcaldías

# def calculateSuburb_v3(text, maybe_cve, image):
def calculateSuburb_v3(row, final_projects):
    # errors = []
    # Es el id de la alcaldía con la cual se encontró una coincidencia.
    sub_id = None

    formatted_data = row.get_formatted_data()
    if not formatted_data:
        return None, None

    normal_name = formatted_data[0]

    # cve --> El id de la Colonia (Suburb) que haya coincidido si se encontró
    # una clave y si coincidió esa clave con lo que había en base de datos.

    # ### esto devuelve el sub_id, no el cve
    sub_id_by_cve = get_cve(normal_name, final_projects, row)
    # Id es el ID de la colonia que encontró a partir del nombre normalizado.
    sub_id = get_suburb_id(normal_name, final_projects, row)

    # El extrañísimo (pero siempre es posible) caso de que existan dos
    # alcaldías distintas en el mismo lugar.
    if sub_id and sub_id_by_cve and sub_id != sub_id_by_cve:
        row.set_errors("Doble coincidencia: por clave y por nombre")
        return sub_id_by_cve, normal_name
    sub_id_by_cve_in_proj = get_cve(formatted_data[1], final_projects, row)
    # Se devuelve la primera coincidencia:
    return sub_id_by_cve or sub_id or sub_id_by_cve_in_proj, normal_name


def get_cve(text, final_projects, row):
    import re
    cve_suburb = None
    sub_id = None
    # identificamos el formato (11-034)
    re_has_cve = re.compile(r'.*(?:\D|^)(\d{2})\s?\D?\s?(\d{3})(?:\D|$).*')
    # Se busca la clave de la colonia
    # el texto puede llegar False
    if not text:
        row.set_errors(u"text Value error: %s" % text)
        return None
    if re.match(re_has_cve, text):
        # Normalizamos el formato para aquello que "parece" clave
        cve_suburb = re.sub(re_has_cve, r'\1-\2', text)
        # sabemos que el id de la alcaldía sólo llega a 16, descartamos lo que
        # sea más grande que eso
        if int(cve_suburb[:2]) < 17:
            try:
                sub_id = final_projects.get(suburb__cve_col=cve_suburb)\
                    .suburb.id
            except Exception:
                err = "Algo que parece clave no se encontró (%s)" % cve_suburb
                row.set_errors(err)
                print 'Clave no encontrada' + cve_suburb
    return sub_id


def get_suburb_id(normal_name, final_projects, row):
    # La búsqueda se hace entre las Colonias que no han tenido coincidencias,
    # para no repetir dos registros idénticos.
    subs_found = final_projects.filter(suburb__short_name=normal_name)
    subs_found_count = subs_found.count()
    if subs_found_count > 1:
        err = u"Varias colonias coincidentes con %s" % normal_name
        row.set_errors(err)
    if subs_found_count:
        return subs_found.first().suburb.id
    else:
        return None

# def saveFinalProjSuburb_v3(sub_id, row_data, simil=1):


def saveFinalProjSuburb_v3(sub_id, row, final_projects, simil=1):
    # from public_account.models import column_types
    from project.models import FinalProject
    try:
        final_proy = final_projects.get(suburb__id=sub_id)
    except FinalProject.DoesNotExist:
        print "No se enontró sub_id en función saveFinalProjSuburb_v3"
        return None
    row.final_project = final_proy
    row.similar_suburb_name = simil
    # for idx, value in enumerate(row_data.get("data")):
    #     if idx:
    #         # print column_types[idx]["field"]
    #         setattr(final_proy, column_types[idx]["field"], value)
    row.save()
    return sub_id


def flexibleMatchSuburb_v3(row, sub_name, final_projects):
    # from pprint import pprint
    from public_account.models import Row
    from difflib import SequenceMatcher
    # print u"----------------flexibleMatchSuburb_v3--------------------"
    if sub_name:
        return
    max_conc = 0
    # sub_id = None
    # match_row_idx = -1
    max_fp = None
    for fp in final_projects:
        concordance = SequenceMatcher(None, fp.suburb.short_name,
                                      sub_name).ratio()
        if Row.objects.filter(final_project=fp).exists():
            concordance -= 0.001
        else:
            print "%s : %s" % (fp.suburb.short_name, concordance)
        if concordance > 0.8 and concordance > max_conc:
            max_fp = fp
            # match_row_idx = row_idx
            # match_row_idx = row.id
            max_conc = concordance
    if max_fp:
        # match_row = orphan_rows[match_row_idx]
        # sub_id = saveFinalProjSuburb_v3(
        saveFinalProjSuburb_v3(
            max_fp.suburb.id, row, final_projects, max_conc)
