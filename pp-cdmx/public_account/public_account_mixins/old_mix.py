# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from geographic.models import Suburb

from scripts.data_cleaner import set_new_error
from scripts.data_cleaner_v2 import calculateNumber


class PublicAccountOldMix:

    def column_formatter(self, reset=False, image_num=None):
        # LUCIAN: Esto es solo la continuación de lo que ya comenzaste
        # Lucian, creo que ya no es necesario importar esto:
        from project.models import FinalProject
        from public_account.models import PPImage
        import numpy
        from pprint import pprint

        # suburbs_dict = []
        is_pa_stable = True
        all_orphan_rows = {"suburbs": [], "numbers": []}
        all_images = PPImage.objects.filter(public_account=self)
        if image_num:
            all_images = all_images.filter(path__icontains=image_num)

        if reset:
            FinalProject.objects\
                .filter(suburb__townhall=self.townhall,
                        period_pp=self.period_pp,
                        image__in=all_images)\
                .update(image=None, similar_suburb_name=None, error_cell="",
                        inserted_data=False, approved=None, modified=None,
                        executed=None, progress=None, variation=None,
                        variables="")
            PPImage.objects.filter(public_account=self)\
                .update(status=None,
                        error_cell=None, len_array_numbers=None,
                        data_row_numbers=None, data_row_suburbs=None)
            self.error_cell = ""
            self.status = None
            self.save()
        for image in all_images:
            print image.path
            ord_suburbs = image.calc_columns('suburbs')

            number_results, len_array = image.calc_columns('numbers')
            standar_dev = numpy.std(len_array)
            if standar_dev > 0:
                print u"vamos a ir por un cálculo estricto"
                number_results_stict, len_array_sctict = image.calc_columns(
                    'numbers', True)
                standar_dev_stict = numpy.std(len_array_sctict)
                if standar_dev_stict < standar_dev:
                    print u"el no estricto es %s" % len_array
                    number_results = number_results_stict
                    len_array = len_array_sctict
                    standar_dev = numpy.std(len_array)
                    image.len_array_numbers = len_array
                    image.data_row_numbers = number_results_stict
                    image.save()
                else:
                    print "no mejora el len_array"
                    print u"el estricto es %s" % len_array_sctict
            print len_array
            if standar_dev <= 0.8:
                ord_numbers = []
                print "la imagen es estable"
                rows_count = int(round(numpy.mean(len_array)))
                image.rows_count = rows_count
                image.save()

                for idx, row in enumerate(xrange(rows_count)):
                    complete_row = {}
                    for idx_amm, ammount in enumerate(amm_types):
                        # curr_res = number_results[idx_amm]
                        """if len(curr_res) > rows_count:
                            strict_res = [x for x in curr_res
                                if x.get("correct_format")]
                            if len(strict_res) == rows_count:
                                number_results[idx_amm] = strict_res
                                set_new_error(image,
                                    "Forzamos el formato
                                    correcto a %s"%ammount)"""

                        try:
                            complete_row[ammount] = number_results[
                                idx_amm][idx]
                        except Exception:
                            # print ammount
                            # print row
                            # print e
                            pass
                    complete_row["seq"] = idx
                    complete_row["image_id"] = image.id
                    ord_numbers.append(complete_row)
                all_orphan_rows = image.comprobate_stability(
                    all_orphan_rows, ord_numbers, ord_suburbs)
            else:
                print "inestable_numbers"
                image.status = "inestable_numbers"
                image.save()
                is_pa_stable = False
                set_new_error(
                    image, u"No todas las columnas numéricas coinciden")
                continue

        if image_num:
            pprint(ord_suburbs)
            if len(ord_numbers):
                print u"*******los números ordenados:**********"
                print len_array
                pprint(ord_numbers)
            print u"*******los números crudos:**********"
            print len_array
            pprint(number_results)
            # return
        if is_pa_stable or True:
            # si existen filas huérfanos:
            len_orphan = len(all_orphan_rows)
            # new_orphan_rows = []
            # subs_alone = None
            new_orphan_subs = None
            if len_orphan:
                print "haremos un match suavizado"
                new_orphan_subs = flexible_match_suburb(all_orphan_rows, self)
                all_orphan_rows["suburbs"] = new_orphan_subs
                # new_orphan_rows = formatter_orphan(
                #     all_images, all_orphan_rows)
                # len_new_orphan = len(new_orphan_rows)

            missings_subs = Suburb.objects.filter(
                townhall=self.townhall,
                finalproject__period_pp=self.period_pp,
                finalproject__image__isnull=True)

            incomp_images = PPImage.objects.filter(public_account=self)\
                .exclude(status="completed")

            self.status = ("incompleted" if incomp_images.count()
                           else "completed")

            if missings_subs.count():
                set_new_error(self, 'Faltan las siguientes Colonias:')
            for sub in missings_subs:
                set_new_error(self, "%s %s" % (sub.cve_col, sub.name))

        if not is_pa_stable:
            self.status = "inestable_images"
        self.save()
        return

    def column_formatter_v2(self, reset=False, image_num=None):
        from project.models import AnomalyFinalProject
        from public_account.models import PPImage
        from classification.models import Anomaly
        print
        print
        print "----Cuenta publica %s, id: %s----" % (self, self.id)
        from scripts.data_cleaner_v2 import (
            saveFinalProjSuburb_v2,
            calculateSuburb_v2)
        # import numpy
        # suburbs_dict = []

        all_images = PPImage.objects.filter(public_account=self)
        if image_num:
            all_images = all_images.filter(path__icontains=image_num)

        if reset:
            self.reset(all_images)

        all_images = all_images.order_by("path")

        # Se obtienen los formatos de cada uno de los
        # variables = self.get_variables()
        special_formats = self.calculate_special_formats(
            all_images, column_types[3:], image_num)

        seq = 1
        """
        Una vez obtenido los valores de special_formats, se tratan los datos:
        """
        if not special_formats:
            # si el calculo de special_formats no trae informacion, crashea
            # todo el proceso, hasta arreglarlo no se procesaran las imagenes
            set_new_error(
                self, "error al calcular special_formats: %s" %
                special_formats)
            set_new_error(
                self, "No se pocreso ningun imagen.table_data")
            all_images = []

        for image in all_images:
            print u"    %s" % image
            # Intentamos obtener los datos que nos interesan
            # print image.path
            # Por cada fila de datos:
            image_table_data = image.get_table_data()
            if not image_table_data:
                set_new_error(
                    self, "La imagen %s no proceso Table Data" % image)
            for row in image_table_data:
                seq += 1
                errors = []
                # Intentamos obtener de forma simple el id de la colonia.
                sub_id, normal_name, errors = calculateSuburb_v2(
                    row[0], row[1], image)
                # final_proj = None
                if sub_id is False:
                    continue

                row_data = []

                for idx, col in enumerate(row):
                    col_ref = column_types[idx]
                    if idx > 2:
                        special_format = special_formats[idx - 3]
                        final_value, c_errors = calculateNumber(
                            col, col_ref, special_format)
                        if len(c_errors):
                            errors += c_errors
                            final_value = None
                    else:
                        final_value = col if idx else normal_name

                    # if not final_proj:
                    row_data.append(final_value)

                all_row = {
                    "seq": seq,
                    "data": row_data,
                    "errors": errors,
                    "image_id": image.id,
                    "raw": row
                }
                new_sub_id = None
                if sub_id:
                    new_sub_id, new_errors = saveFinalProjSuburb_v2(
                        sub_id, all_row)
                if not new_sub_id:
                    orphan_rows = self.get_orphan_rows()
                    orphan_rows.append(all_row)
                    self.orphan_rows = json.dumps(orphan_rows)
                    self.save()

        all_orphan_rows = self.get_orphan_rows()
        # if image_num:
        #     print u"*******las filas no insertadas:**********"
        #     print all_orphan_rows

        # si existen filas huérfanos:
        len_orphan = len(all_orphan_rows)
        # new_orphan_rows = []
        # subs_alone = None
        # new_orphan_subs = None
        if len_orphan:
            pass
            # print "haremos un match suavizado"
            # inconsistencia de tipos en la logica, no se pudo deducir
            # new_orphan_rows = flexibleMatchSuburb_v2(all_orphan_rows, self)
            # len_new_orphan = len(new_orphan_rows)

        missings_subs = Suburb.objects.filter(
            townhall=self.townhall,
            finalproject__period_pp=self.period_pp,
            finalproject__image__isnull=True)

        incomp_images = PPImage.objects.filter(public_account=self)\
            .exclude(status="completed")

        self.status = "incompleted" if incomp_images.count() else "completed"

        if missings_subs.count():
            """
            agregar anomalia al proyecto final:
            Anomalía: name="Sin coincidencia en nombre de colonia",
            is_public=False
            """
            anomaly_obj, is_created = Anomaly.objects\
                .get_or_create(name="Sin coincidencia en nombre de colonia")
            anomaly_obj.is_public = False
            anomaly_obj.save()
            anomaly_final_project, is_created = AnomalyFinalProject.objects\
                .get_or_create(
                    anomaly=anomaly_obj,
                    public_account=self,
                )

            set_new_error(self, 'Faltan las siguientes Colonias:')
        for sub in missings_subs:
            # agregar anomalia
            set_new_error(self, "%s %s" % (sub.cve_col, sub.name))

        self.save()
        return

amm_types = ["progress", "approved", "modified", "executed", "variation"]

column_types = [
    {
        "name": "suburb",
        "title": u"Colonia",
        "type": "fk"
    },
    {
        "name": "project",
        "title": u"Proyecto",
        "field": "project_name",
        "type": "text"
    },
    {
        "name": "description",
        "title": u"Descripción",
        "field": "description",
        "type": "text"
    },
    {
        "name": "progress",
        "title": u"Avance",
        "field": "progress",
        "type": "number"
    },
    {
        "name": "approved",
        "title": u"Aprobado",
        "field": "approved",
        "type": "ammount"
    },
    {
        "name": "modified",
        "title": u"Modificado",
        "field": "modified",
        "type": "ammount"
    },
    {
        "name": "executed",
        "title": u"Ejecutado",
        "field": "executed",
        "type": "ammount"
    },
    {
        "name": "variation",
        "title": u"Variación",
        "field": "variation",
        "type": "number"
    },
]


def append_comprob(comprobs, row, name):
    try:
        comprobs.append({"value": row[name], "name": name})
    except Exception:
        pass
    return comprobs


# v3 Borrar
def similar_content(sub_name, row):
    from difflib import SequenceMatcher
    comprobs = append_comprob([], row, "curr")
    if row.get("can_be_comb"):
        comprobs = append_comprob(comprobs, row, "comb")
        if row.get("can_be_triple"):
            comprobs = append_comprob(comprobs, row, "triple")
    may_name = None
    max_value = 0
    for comp in comprobs:
        curr_max = max(
            SequenceMatcher(None, sub_name, comp["value"]).ratio(),
            SequenceMatcher(None, comp["value"], sub_name).ratio())
        if curr_max > max_value:
            max_value = curr_max
            may_name = comp["name"]

    return may_name, max_value


# v3 Borrar
def flexible_match_suburb(orphan_subs, pa):
    from scripts.data_cleaner import saveFinalProjSuburb
    from public_account.models import PPImage
    print u"------------------------------------"
    # print orphan_subs
    missing_row_idxs = [idx for idx, x in enumerate(
        orphan_subs) if not x["suburb_id"]]
    missings_subs = Suburb.objects.filter(
        townhall=pa.townhall,
        finalproject__period_pp=pa.period_pp,
        finalproject__image__isnull=True)
    for sub in missings_subs:
        max_conc = 0
        final_row_idx = -1
        for row_idx in missing_row_idxs:
            if orphan_subs[row_idx]["invalid"]:
                continue
            may, concordance = similar_content(
                sub.short_name, orphan_subs[row_idx])
            # print "%s -- %s"%(may, concordance)
            if concordance > 0.8 and concordance > max_conc:
                final_row_idx = row_idx
                may_type = may
                # comb_bigger = may == 'comb'
                # triple_bigger = may == 'triple'
                max_conc = concordance
        if final_row_idx > -1:
            # print final_row_idx
            sel_row = orphan_subs[final_row_idx]
            image_id = sel_row["image_id"]
            image = PPImage.objects.get(id=image_id)
            sub_id = saveFinalProjSuburb(sub.id, image, max_conc)
            # print "-------------"
            # print sub_id
            if sub_id:
                orphan_subs[final_row_idx]["suburb_id"] = sub.id
                orphan_subs[final_row_idx]["concordance"] = max_conc
                orphan_subs[final_row_idx]["type_comb"] = may_type
                if may_type != 'curr':
                    orphan_subs = set_values_combs(
                        orphan_subs, sel_row, image, may_type)
            else:
                set_new_error(
                    image,
                    "No se encontró el sub %s que ya habíamos seteado"
                    % sub.id)
        # else:
            # print sub.short_name
    return orphan_subs


def set_values_combs(orphan_subs, sel_row, image, may_type):
    is_triple = may_type == 'triple'
    all_next = [1, 2] if is_triple else [1]
    for next_req in all_next:
        try:
            id_next = [idx for idx, x in enumerate(orphan_subs)
                       if x.get("image_id") == image.id and
                       x.get("seq") == sel_row.get("seq") + next_req]
            if len(id_next):
                orphan_subs[id_next[0]]["invalid"] = True
            else:
                # print "No existieron coincidencias..."
                pass
        except Exception as e:
            set_new_error(
                image,
                u"No se encontró el seq %s para ponerlo como ínválido")
            print e
    return orphan_subs
