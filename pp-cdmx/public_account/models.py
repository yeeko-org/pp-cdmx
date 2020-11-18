# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from geographic.models import TownHall, Suburb
from period.models import PeriodPP
from pprint import pprint
from scripts.data_cleaner import set_new_error
import json

from scripts.data_cleaner_v2 import calculateNumber

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
        "field": "final_name",
        "type": "text"
    },
    {
        "name": "description",
        "title": u"Descripción",
        "field": "description_cp",
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
        

class PublicAccount(models.Model):
    # original_pdf = models.FileField(
    #     upload_to="public_account",
    #     blank=True,
    #     null=True,
    #     verbose_name=u"PDF original")
    VERTICAL_ALIGN_AMMOUNTS = (
        ("top", u"top"),
        ("center", u"center"),
        ("bottom", u"bottom"),
    )
    townhall = models.ForeignKey(
        TownHall,
        blank=True,
        null=True,
        verbose_name=u"Alcaldía")
    # pages = models.TextField(blank=True, null=True, verbose_name=u"Paginas")
    period_pp = models.ForeignKey(PeriodPP, verbose_name=u"Periodo PP")
    variables = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=80, default=u"uncleaned",
        blank=True, null=True)
    error_cell = models.TextField(
        blank=True, null=True,
        verbose_name="pila de errores")
    orphan_rows = models.TextField(
        blank=True, null=True,
        verbose_name="Filas no insertadas")

    approved = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True,
        verbose_name=u"Aprobado")
    modified = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True,
        verbose_name=u"Modificado")
    executed = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True,
        verbose_name=u"Ejecutado")

    vertical_align_ammounts = models.CharField(
        choices=VERTICAL_ALIGN_AMMOUNTS,
        max_length=50,
        blank=True, null=True)

    def __unicode__(self):
        return u"%s -- %s" % (self.period_pp, self.townhall)

    def reset(self, all_images=None):
        from project.models import FinalProject

        query_final_p=FinalProject.objects\
            .filter(suburb__townhall=self.townhall,
                    period_pp=self.period_pp)
        if all_images:
            query_final_p.filter(image__in=all_images)

        query_final_p.update(
            image=None, similar_suburb_name=None, error_cell="",
            inserted_data=False, approved=None, modified=None,
            executed=None, progress=None, variation=None)

        PPImage.objects.filter(public_account=self)\
            .update(status=None, error_cell=None, len_array_numbers=None,
                    data_row_numbers=None, data_row_suburbs=None)

        self.error_cell = ""
        self.status = None
        self.save()

    def column_formatter(self, reset=False, image_num=None):
        # LUCIAN: Esto es solo la continuación de lo que ya comenzaste
        # Lucian, creo que ya no es necesario importar esto:
        from project.models import FinalProject
        import numpy
        from pprint import pprint

        suburbs_dict = []
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
            ord_suburbs = image.calcColumns('suburbs')

            number_results, len_array = image.calcColumns('numbers')
            standar_dev = numpy.std(len_array)
            if standar_dev > 0:
                print u"vamos a ir por un cálculo estricto"
                number_results_stict, len_array_sctict = image.calcColumns(
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
                        #curr_res = number_results[idx_amm]
                        """if len(curr_res) > rows_count:
                            strict_res = [x for x in curr_res
                                if x.get("correct_format")]
                            if len(strict_res) == rows_count:
                                number_results[idx_amm] = strict_res
                                set_new_error(image,
                                    "Forzamos el formato correcto a %s"%ammount)"""

                        try:
                            complete_row[ammount] = number_results[
                                idx_amm][idx]
                        except Exception as e:
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
            new_orphan_rows = []
            subs_alone = None
            new_orphan_subs = None
            if len_orphan:
                print "haremos un match suavizado"
                new_orphan_subs = flexibleMatchSuburb(all_orphan_rows, self)
                all_orphan_rows["suburbs"] = new_orphan_subs
                new_orphan_rows = formatter_orphan(
                    all_images, all_orphan_rows)
                len_new_orphan = len(new_orphan_rows)

            missings_subs = Suburb.objects.filter(
                townhall=self.townhall,
                finalproject__period_pp=self.period_pp,
                finalproject__image__isnull=True)

            incomp_images = PPImage.objects.filter(public_account=self)\
                .exclude(status="completed")

            self.status = "incompleted" if incomp_images.count() else "completed"

            if missings_subs.count():
                set_new_error(self, 'Faltan las siguientes Colonias:')
            for sub in missings_subs:
                set_new_error(self, "%s %s" % (sub.cve_col, sub.name))

        if not is_pa_stable:
            self.status = "inestable_images"
        self.save()
        return

    def column_formatter_v2(self, reset=False, image_num=None):
        from project.models import FinalProject
        from scripts.data_cleaner_v2 import (
            saveFinalProjSuburb_v2, calculateSuburb_v2)
        import numpy
        suburbs_dict = []

        all_images = PPImage.objects.filter(public_account=self)
        if image_num:
            all_images = all_images.filter(path__icontains=image_num)

        if reset:
            self.reset(all_images)

        #Se obtienen los formatos de cada uno de los 
        variables = self.get_variables()
        special_formats = self.calculate_special_formats(
            all_images, column_types[3:])

        print special_formats


        seq = 1
        #Una vez obtenido los valores de special_formats, se tratan los datos:
        for image in all_images:
            #Intentamos obtener los datos que nos interesan
            #print image.path
            #Por cada fila de datos:
            for row in image.get_table_data():
                seq+=1
                errors = []
                #Intentamos obtener de forma simple el id de la colonia.
                sub_id, normal_name, errors = calculateSuburb_v2(
                    row[0], row[1], image)
                final_proj = None
                if sub_id == False:
                    continue
                
                row_data = []

                for idx, col in enumerate(row):
                    col_ref = column_types[idx]
                    if idx > 2:
                        special_format = special_formats[idx-3]
                        final_value, c_errors = calculateNumber(col, col_ref, special_format)
                        if len(c_errors):
                            errors+=c_errors
                            final_value = None
                    else:
                        final_value = col if idx else normal_name

                    #if not final_proj:
                    row_data.append(final_value)
                    if idx and final_value:
                        pass
                        ###final_proj[col_ref["field"]] = final_value

                all_row = {
                    "seq": seq, 
                    "data": row_data,
                    "errors": errors, 
                    "image": image
                }
                new_sub_id = None
                if sub_id:
                    new_sub_id, new_errors = saveFinalProjSuburb_v2(sub_id, all_row)
                if not new_sub_id:
                    orphan_rows = self.get_orphan_rows()
                    orphan_rows.append(row_data)
                    self.orphan_rows = json.dumps(orphan_rows)
                    self.save()

        all_orphan_rows = self.get_orphan_rows()
        if image_num:
            print u"*******las filas no insertadas:**********"
            print all_orphan_rows
   
        # si existen filas huérfanos:
        len_orphan = len(all_orphan_rows)
        new_orphan_rows = []
        subs_alone = None
        new_orphan_subs = None
        if len_orphan:
            print "haremos un match suavizado"
            ### inconsistencia de tipos en la logica, no se pudo deducir 
            # orphan_subs = all_orphan_rows["suburbs"]
            # new_orphan_subs = flexibleMatchSuburb_v2(orphan_subs, self)
            # all_orphan_rows["suburbs"] = new_orphan_subs
            # new_orphan_rows = formatter_orphan(
            #     all_images, all_orphan_rows)
            # len_new_orphan = len(new_orphan_rows)

        missings_subs = Suburb.objects.filter(
            townhall=self.townhall,
            finalproject__period_pp=self.period_pp,
            finalproject__image__isnull=True)

        incomp_images = PPImage.objects.filter(public_account=self)\
            .exclude(status="completed")

        self.status = "incompleted" if incomp_images.count() else "completed"

        if missings_subs.count():
            set_new_error(self, 'Faltan las siguientes Colonias:')
        for sub in missings_subs:
            set_new_error(self, "%s %s" % (sub.cve_col, sub.name))

        self.save()
        return

    def calculate_special_formats(self, all_images, columns_nums):
        variables = self.get_variables()
        #si ya se había canculado el special_formats, simplemente se obtiene
        # if "special_formats" in variables:
        #     return variables["special_formats"]

        #si no, se calcula:
        #Se trabajará solo con las columnas numéricas, que son las últimas 5
        count_rows = [0, 0, 0, 0, 0]
        special_format_count = [0, 0, 0, 0, 0]
        special_formats = []
        for image in all_images:
            print image
            for row in image.get_table_data():
                #Se trabajarán solo con los últimos tres datos
                ####Se trabajarán solo con los últimos 5 datos
                for idx, value in enumerate(row[3:]):
                    sum_col = calculateNumber(value, columns_nums[idx])
                    #Solo se sumarán si la función arrojó algún número
                    if sum_col != None:
                        special_format_count[idx]+=sum_col
                        count_rows[idx]+=1

            #Se puede detarminar una tendencia de tener algún formato especial
            #si existen al menos 5 datos con formato válido
            if min(count_rows) > 4:### or image_num:
                for idx, col in enumerate(columns_nums):
                    is_special = special_format_count[idx] / float(count_rows[idx]) >= 0.75
                    special_formats.append(is_special)
                break
        variables["special_formats"] = special_formats
        self.variables = json.dumps(variables)
        self.save()
        return special_formats



    def get_variables(self):
        import json
        try:
            return json.loads(self.variables)
        except Exception as e:
            print("self.variables No JSON object could be decoded, "
                  "se reiniciara a { }")
            return {}

    def get_orphan_rows(self):
        import json
        try:
            return json.loads(self.orphan_rows)
        except Exception as e:
            print("self.orphan_rows No JSON object could be decoded, "
                  "se reiniciara a []")
            return []

    class Meta:
        verbose_name = u"Cuenta Publica"
        verbose_name_plural = u"Cuentas Publicas"


class PPImage(models.Model):
    public_account = models.ForeignKey(PublicAccount)
    path = models.CharField(max_length=255)
    json_variables = models.TextField(blank=True, null=True)
    vision_data = models.TextField(blank=True, null=True)
    clean_data = models.TextField(blank=True, null=True)
    error_cell = models.TextField(
        blank=True, null=True, verbose_name="pila de errores")
    len_array_numbers = models.CharField(
        max_length=80, blank=True, null=True)
    data_row_numbers = models.TextField(
        blank=True, null=True, verbose_name=u"Datos de columnas numéricas")
    data_row_suburbs = models.TextField(
        blank=True, null=True, verbose_name=u"Datos de columna de suburbs")
    status = models.CharField(
        blank=True, null=True, max_length=80, default=u"uncleaned")

    def get_first_image(self):
        if "0001" in self.path:
            return self
        else:
            return PPImage.objects.filter(
                public_account=self.public_account,
                path__icontains="0001",
            ).first()

    def get_data_full_image(self):
        self.find_reference_blocks()
        self.calculate_columns_bot()
        self.calculate_column_boxs()
        self.get_data_from_columns()
        #self.cleand_columns_numbers()

    def find_block(self, text=False, regex=False, full_obj=False, lines=False):
        from scripts.data_cleaner import similar
        import re
        vision_data = self.get_vision_data().get("full", {})
        first_opcion = False
        opcion = []
        for block in vision_data:
            complete_w = block.get("w", "")

            if text:
                if lines:
                    for line in complete_w.split("\n"):
                        similar_value = similar(text.lower(), line.lower())
                        if similar_value > 0.7:
                            opcion.append(
                                {
                                    "block": block,
                                    "similar_value": similar_value
                                }
                            )

                else:
                    similar_value = similar(text.lower(), complete_w.lower())
                if similar_value > 0.7:
                    opcion.append(
                        {
                            "block": block,
                            "similar_value": similar_value
                        }
                    )
                # if text.lower() in complete_w.lower():
                #     print block.get("w")
                #     if full:
                #         return block
                #     else:
                #         return {
                #             "vertices": block.get("vertices"),
                #             "w": block.get("w"),
                #         }

            elif regex:
                x = re.search(regex, complete_w)
                if x:
                    opcion.append(
                        {
                            "block": block,
                            "similar_value": 1
                        }
                    )

        if not opcion:
            return False

        def block_value(e):
            return e['similar_value']
        opcion.sort(key=block_value)

        for o in opcion:
            w = o.get("block").get("w")
            value = o.get("similar_value")

        best_opcion = opcion[-1]
        block = best_opcion.get("block")
        similar_value = best_opcion.get("similar_value")
        if full_obj:
            block["similar_value"] = similar_value
            return block
        else:
            return {
                "vertices": block.get("vertices"),
                "w": block.get("w"),
                "similar_value": similar_value
            }

    def find_max_left(self, top=0, bot=1750):
        vision_data = self.get_vision_data().get("full", {})
        left = 300

        for block in vision_data:
            vertices = block.get("vertices")
            if vertices[0].get("y") < top or vertices[2].get("y") > bot:
                continue
            block_left = vertices[0].get("x")
            if block_left < left:
                left = block_left
        return left

    def find_reference_blocks(self):
        self.find_block_logo()
        self.find_block_unidad()
        self.find_block_title()
        self.find_block_ppd()
        self.find_block_ammounts()
        self.find_headers()

    def find_block_logo(self):
        block_logo = self.find_block(
            "gobierno de la ciudad de mexico")

        if not block_logo:
            block_logo = self.find_block(
                "ciudad de mexico")
        if block_logo:
            vertices = block_logo.get("vertices")
            data = self.get_json_variables()
            #data["logo"] = first_opcion

            data["logo_left"] = vertices[0].get("x")
            data["logo_bot"] = vertices[3].get("y")
            self.json_variables = json.dumps(data)
            self.save()
        else:
            print u"no se encontro el data_left"

    def find_block_unidad(self):
        block_unidad = self.find_block(
            u"unidad responsable del gasto: %s"%
            self.public_account.townhall.name )
        if not block_unidad:
            block_unidad = self.find_block(
                u"unidad responsable del gasto")
        if not block_unidad:
            # considerar otras medidas como variantes
            return
        data = self.get_json_variables()
        data["unidad_bot"] = block_unidad.get("vertices")[3].get("y")
        data["data_left"] = block_unidad.get("vertices")[0].get("x")
        self.json_variables = json.dumps(data)
        self.save()

    def find_block_title(self):
        block_title = self.find_block(
            "cuenta publica de la ciudad de mexico %s" %
            (self.public_account.period_pp.year))
        if not block_title:
            # considerar otras medidas como variantes
            return
        data = self.get_json_variables()
        #data["block_title"] = block_title
        data["title_rigth"] = block_title.get("vertices")[1].get("x")
        self.json_variables = json.dumps(data)
        self.save()

    def find_block_ppd(self):
        block_ppd = self.find_block(
            "ppd presupuesto participativo para las delegaciones")
        if not block_ppd:
            # considerar otras medidas como variantes
            return
        data = self.get_json_variables()
        #data["block_ppd"] = block_ppd

        block_ppd_rigth = block_ppd.get("vertices")[1].get("x")
        block_ppd_left = block_ppd.get("vertices")[0].get("x")
        data["data_center"] = (block_ppd_rigth + block_ppd_left) / 2
        self.json_variables = json.dumps(data)
        self.save()

    def find_block_ammounts(self):
        block_ammounts = self.find_block(
            "presupuesto (pesos con dos decimales")
        if not block_ammounts:
            # considerar otras medidas como variantes
            return
        data = self.get_json_variables()
        #data["block_ammounts"] = block_ammounts

        block_ammounts_rigth = block_ammounts.get("vertices")[1].get("x")
        block_ammounts_left = block_ammounts.get("vertices")[0].get("x")
        data["ammounts_center"] = (
            block_ammounts_rigth + block_ammounts_left) / 2
        self.json_variables = json.dumps(data)
        self.save()

    def find_headers(self):
        import re
        colonia = self.find_block(u"colonia o pueblo originario")
        proyecto = self.find_block(u"proyecto")
        descripcion = self.find_block(u"descripción")
        avance = self.find_block(u"avance del proyecto")
        if not avance:
            avance = self.find_block(u"del proyecto")
            if not avance:
                avance = self.find_block(regex=r'Proyecto(?:$|\s\S+)?')

        aprobado = self.find_block(u"aprobado")
        # --------------------------------------------------------------------
        # ajuste de ancho en aprovacion
        if aprobado:
            text_aprobado = aprobado.get("w")
            if text_aprobado:
                # se espera un asterisco obligatorio despues de Aprobado
                x = re.search(r'Aprobado( )*(\*)', text_aprobado)
                print text_aprobado
                if not x:
                    print "se le agrego variacion de 10 pixeles"
                    vertices = aprobado.get("vertices")
                    p1 = vertices[1]
                    p2 = vertices[2]
                    p1["x"] = p1["x"] + 10
                    p2["x"] = p2["x"] + 10
                    aprobado["vertices"] = [vertices[0], p1, p2, vertices[3]]
                else:
                    print "no se le agrego variacion"
                print
        # --------------------------------------------------------------------
        modificado = self.find_block(u"modificado")
        ejercido = self.find_block(u"ejercido")
        variacion = self.find_block(u"variación")
        # --------------------------------------------------------------------
        # ajuste de ancho en variacion
        if variacion:
            text_variacion = variacion.get("w").strip()
            if text_variacion:
                # el porciento puede ser con salto de linea
                x = re.search(r'Variación(\s)*(%|\$)', text_variacion)
                print text_variacion
                if not x:
                    print "se le agrego variacion de 20 pixeles"
                    vertices = variacion.get("vertices")
                    p1 = vertices[1]
                    p2 = vertices[2]
                    p1["x"] = p1["x"] + 20
                    p2["x"] = p2["x"] + 20
                    variacion["vertices"] = [vertices[0], p1, p2, vertices[3]]
                else:
                    print "no se le agrego variacion"
                print
        # --------------------------------------------------------------------

        data = self.get_json_variables()
        data["columns_heades"] = [
            colonia,
            proyecto,
            descripcion,
            avance,
            aprobado,
            modificado,
            ejercido,
            variacion,
        ]

        # {
        #     "colonia": colonia,
        #     "proyecto": proyecto,
        #     "descripcion": descripcion,
        #     "avance": avance,
        #     "aprobado": aprobado,
        #     "modificado": modificado,
        #     "ejercido": ejercido,
        #     "variacion": variacion,
        # }

        self.json_variables = json.dumps(data)
        self.save()

    def calculate_column_boxs(self):
        data = self.get_json_variables()
        columns_heades = data.get("columns_heades", [])
        data_left = data.get("data_left")

        columns_top = 0
        if data.get("logo_bot"):
            columns_top = data.get("logo_bot")
        if data.get("unidad_bot"):
            columns_top = data.get("unidad_bot")

        if all([not header for header in columns_heades]):
            print "no se encontraron las cabezeras"
            """
            no tiene cabezeras, se estima que tampoco tendra unidad, asi que
            se tendra que calcular los margnes apartir de los margenes
            del first_image 0001
            """
            first_image = self.get_first_image()
            first_image_data = first_image.get_json_variables()
            first_logo_left = first_image_data.get("logo_left")
            first_title_rigth = first_image_data.get("title_rigth")

            logo_left = data.get("logo_left")
            title_rigth = data.get("title_rigth")
            columns_bot = data.get("columns_bot")

            full_first = first_title_rigth - first_logo_left
            full = title_rigth - logo_left
            dimension_percentage = float(full) / float(full_first)

            first_headers = first_image_data.get("columns_heades", [])

            data_left = self.find_max_left(columns_top, columns_bot)

            first_data_left = first_image_data.get("data_left")
            if not first_data_left:
                print "No se tiene calculado el data_left en 0001"
                return

            desfase = first_data_left - int(
                float(data_left) / dimension_percentage)
            columns_heades = []
            for ref_header in first_headers:
                ref_vertices = ref_header.get("vertices")

                x_left = int((ref_vertices[0].get("x") - desfase) *
                             dimension_percentage)
                x_right = int((ref_vertices[1].get("x") - desfase) *
                             dimension_percentage)

                columns_heades.append(
                    {"vertices": [
                        {"x": x_left},
                        {"x": x_right},
                        {"x": x_right}]}
                )

        elif not data_left:
            print "No se tiene calculado el data_left"
            print "calculando data_left con los datos de first_image 0001"

            if columns_heades and all(columns_heades):
                first_image = self.get_first_image()
                first_image_data = first_image.get_json_variables()
                first_data_left = first_image_data.get("data_left")
                if not first_data_left:
                    print "No se tiene calculado el data_left en 0001"
                    return
                first_logo_left = first_image_data.get("logo_left")
                first_title_rigth = first_image_data.get("title_rigth")
                logo_left = data.get("logo_left")
                title_rigth = data.get("title_rigth")

                full_first = first_title_rigth - first_logo_left
                full = title_rigth - logo_left
                dimension_percentage = float(full) / float(full_first)

                data_left = logo_left - int(
                    (first_logo_left - first_data_left) * dimension_percentage)
            else:
                print "se esperava en columns_heades una lista llena"
                return

        if not len(columns_heades) == 8:
            print u"se esperava una lista de 8 elementos"
            print u"actualemnte tiene: %s" % len(columns_heades)
            return
        elif not all(columns_heades):
            print "el find_headers no encontro todas las cabezeras"
            return
        columns_boxs = []

        for header in columns_heades:

            vertices = header.get("vertices")
            center = (vertices[0].get("x") + vertices[1].get("x")) / 2
            # center=(vertices[0].get("x") + vertices[1].get("x")
            #     + vertices[2].get("x") + vertices[3].get("x"))/4

            radio = center - data_left
            right_data = center + radio

            columns_boxs.append({
                "left": data_left,
                "center": center,
                "right": right_data
            })

            data_left = right_data
            if len(vertices)>2:
                header_bot = vertices[2].get("y")
                if header_bot > columns_top:
                    columns_top = header_bot

        data["columns_boxs"] = columns_boxs
        data["columns_top"] = columns_top
        self.json_variables = json.dumps(data)
        self.save()
        print columns_boxs

    def calculate_columns_bot(self):
        # alto maximo del archivo entre 1700 y 1750
        columns_bot = 1750

        def compare_block_bot(columns_bot, block, similar_min=0):
            if block:
                similar_value = block.get("similar_value")
                if similar_value > similar_min:
                    vertices = block.get("vertices")
                    if columns_bot > vertices[0].get("y"):
                        columns_bot = vertices[0].get("y")
            return columns_bot

        # busqueda del bloque de firmas
        block_elaboro = self.find_block("Elaboro :", lines=True)
        columns_bot = compare_block_bot(columns_bot, block_elaboro, 0.8)
        block_elaboro_re = self.find_block(
            regex=r'(REFIERE|REMANENTE|AUTORI|ELABOR|LABORADO|DIRECTOR)')
        columns_bot = compare_block_bot(columns_bot, block_elaboro_re)

        block_autorizo = self.find_block("Autorizo :", lines=True)
        columns_bot = compare_block_bot(columns_bot, block_autorizo, 0.8)

        # busqueda de la palabra total
        block_total_urg = self.find_block("total urg")
        columns_bot = compare_block_bot(columns_bot, block_total_urg, 0.8)

        block_total = self.find_block("total")
        columns_bot = compare_block_bot(columns_bot, block_total, 0.8)

        # agregar a los calculos

        data = self.get_json_variables()
        data["columns_bot"] = columns_bot
        self.json_variables = json.dumps(data)
        self.save()

    def get_data_from_columns(self):

        data = self.get_json_variables()
        columns_bot = data.get("columns_bot")
        columns_top = data.get("columns_top")
        columns_boxs = data.get("columns_boxs")
        columns_data = []

        for column_box in columns_boxs:
            left = column_box.get("left")
            right = column_box.get("right")
            data_in_block = self.get_blocks_in_box(
                left, right, columns_top, columns_bot)
            columns_data.append(
                [
                    {
                        "w": line.get("w"),
                        "vertices": line.get("vertices")
                    }
                    for line in data_in_block]
            )
        data["columns_data"] = columns_data
        self.json_variables = json.dumps(data)
        self.save()

    def cleand_columns_numbers(self):
        from scripts.data_cleaner import similar
        import re
        data = self.get_json_variables()
        columns_data = data["columns_data"]
        invalids_values = ["1", "2", "3", "3/1"]
        for column_index in [3, 4, 5, 6, 7]:
            approved_data = []
            for number_data in columns_data[column_index]:
                invalid = False
                w = number_data.get("w")
                vertices = number_data.get("vertices")
                for invalid_value in []:
                    similar_value = similar(w, invalid_value)
                    if similar_value > 0.5:
                        invalid = True
                        break

                if invalid:
                    continue

                approved_data.append({
                    "w": w,
                    "vertices": vertices
                })
            columns_data[column_index] = approved_data
        # eliminacion de el primer dato si es un numero entre parentesis

        for column_data in columns_data:
            if not column_data:
                continue
            first_line = column_data[0].get("w")
            x = re.search(r'^\( *\d *\)\n?', first_line)
            if x:
                ignore = column_data.pop(0)

        data["columns_data"] = columns_data
        self.json_variables = json.dumps(data)
        self.save()

    """-----------------------------------------------------------------------
        se espera que en este punto ya se tenga calculado la primera vercion de
        los datos por cada columna, los bloque internos estan limitados a una
        linea, siedo los mas reelevantes las ultimas 5 columnas, quienes se
        garantisa siempre tendran una sola linea y entre ellas existe una
        alineacion horizontal, sin embargo es posibble que en algunos casos se
        encuentre un vlor  "-" que no se identifique, o un dato extra en las
        esquinas como folios o campos no identificados, para lo cual se usara
        un sistema simple de seleccion de la mejor columna
    -----------------------------------------------------------------------"""

    def calculate_reference_column(self, columns_data_top, columns_data_bot):
        """
        nuevo enfoque, usando todos los numero disponibles dentro de los
        limites columns_data_top y columns_data_bot con magen de error de 20px
        se unificaran todos los bloques de numeros omitiendo los que se
        traslapen.

        en un ambiente optimo, la primera columna llenara todos los huecos y 
        las demas columnas se omitiran por traslape, pero si se tiene perdida
        de datos, las filas que falten se llenaran con las demas columnas,
        cuando no se encuentre traslape.
        """
        columns_data_top -=20
        columns_data_bot +=20
        data = self.get_json_variables()
        columns_data = data["columns_data"]
        reference_column = []
        for index in range(3, 8):
            for block in columns_data[index]:

                block_vertices = block.get("vertices")
                b_top = block_vertices[0].get("y")
                b_bot = block_vertices[2].get("y")
                if not (b_top>columns_data_top and b_bot<columns_data_bot):
                    continue

                overlap=False
                for ref_block in reference_column:
                    # revisar si se traslapa con el presente, si es asi, continuar
                    ref_block_vertices = ref_block.get("vertices")
                    rb_top = ref_block_vertices[0].get("y")
                    rb_bot = ref_block_vertices[2].get("y")

                    over_ref = b_top< rb_top and b_bot<rb_top
                    below_ref = b_top> rb_bot and b_bot>rb_bot

                    if not (over_ref or below_ref):
                        overlap=True
                        break

                if not overlap:
                    reference_column.append(block)

        def block_vertice_y(block):
            return block["vertices"][0].get("y")

        reference_column.sort(key=block_vertice_y)

        data["reference_column"] = reference_column
        self.json_variables = json.dumps(data)
        self.save()
        return reference_column



        # columns_counts = {}

        # for index in range(3, 8):
        #     print index
        #     column_leng = len(columns_data[index])
        #     print column_leng
        #     if column_leng in columns_counts:
        #         columns_counts[column_leng]["count"] += 1
        #         columns_counts[column_leng]["columns"].append(index)
        #     else:
        #         columns_counts[column_leng] = {
        #             "count": 1,
        #             "columns": [index]
        #         }
        #     print columns_counts
        #     print
        # normal_counts = sorted([key for key, value in columns_counts.items()])
        # print normal_counts
        # normal_count = normal_counts[0]
        # best_column_index = columns_counts[normal_count]["columns"][0]

        # data["best_column_index"] = best_column_index
        # self.json_variables = json.dumps(data)
        # self.save()
        # return best_column_index

    def calculate_columns_data_top(self):
        data = self.get_json_variables()
        columns_data = data["columns_data"]
        row_0_y = columns_data[0][0].get("vertices")[0].get("y")
        row_1_y = columns_data[1][0].get("vertices")[0].get("y")
        row_2_y = columns_data[2][0].get("vertices")[0].get("y")

        # el limite superior de el dato mas alto con un ajuste de -5 pixeles
        row_x_y = row_0_y if row_0_y < row_1_y else row_1_y
        data["columns_data_top"] = row_x_y if row_x_y < row_2_y else row_2_y
        data["columns_data_top"] -= 5
        self.json_variables = json.dumps(data)
        self.save()
        return data["columns_data_top"]

    def calculate_columns_data_bot(self):
        data = self.get_json_variables()
        columns_data = data["columns_data"]
        row_0_y = columns_data[0][-1].get("vertices")[2].get("y")
        row_1_y = columns_data[1][-1].get("vertices")[2].get("y")
        row_2_y = columns_data[2][-1].get("vertices")[2].get("y")

        # el limite superior de el dato mas alto con un ajuste de -5 pixeles
        row_x_y = row_0_y if row_0_y > row_1_y else row_1_y
        data["columns_data_bot"] = row_x_y if row_x_y > row_2_y else row_2_y
        data["columns_data_bot"] += 5
        self.json_variables = json.dumps(data)
        self.save()
        return data["columns_data_bot"]

    def calculate_table_data(self, limit_position="top"):
        data = self.get_json_variables()
        if not all(data["columns_data"]):
            print "se esperava 8 columnas, todas con datos"
            return
        columns_data_top = data.get(
            "columns_data_top", self.calculate_columns_data_top())
        columns_data_bot = data.get(
            "columns_data_bot", self.calculate_columns_data_bot())
        reference_column = data.get(
            "reference_column", self.calculate_reference_column(
                columns_data_top, columns_data_bot))

        if limit_position == "top":
            vertical_limits = self.box_limits_top(
                reference_column, columns_data_top, columns_data_bot
            )

        elif limit_position == "center":
            vertical_limits = self.box_limits_center(
                reference_column, columns_data_top, columns_data_bot
            )

        elif limit_position in ["bot", "bottom"]:
            vertical_limits = self.box_limits_bot(
                reference_column, columns_data_top, columns_data_bot
            )
        else:
            return

        columns_data = data.get("columns_data")

        table_data = []

        for vertical_limit in vertical_limits:
            row_top = vertical_limit.get("top")
            row_bot = vertical_limit.get("bot")
            row_data = []
            for column_data in columns_data:
                row_blocks = []
                for block in column_data:
                    vertices = block.get("vertices")
                    block_top = vertices[0].get("y")
                    block_bot = vertices[3].get("y")

                    if block_top >= row_top and block_bot <= row_bot:
                        # palabra completos dentro de los limites
                        row_blocks.append(block)
                        continue

                    full = block_bot - block_top
                    if (block_top >= row_top and block_top <= row_bot):
                        # porcion atravezada por bot
                        fraccion = row_bot - block_top
                    elif(block_bot >= row_top and block_bot <= row_bot):
                        # porcion atravezada por top
                        fraccion = block_bot - row_top
                    elif row_top >= block_top and row_bot <= block_bot:
                        # la linea atravieza los limites, se deve contemplar?
                        row_blocks.append(block)
                        continue
                    else:
                        continue
                    porcentaje = (fraccion * 100) / full
                    if porcentaje > 60:
                        row_blocks.append(block)

                line_text = u" ".join(
                    [line.get("w") for line in row_blocks])
                line_text = line_text.replace(u"\n", " ").strip()
                row_data.append(line_text)

            table_data.append(row_data)

        data["table_data"] = table_data
        self.json_variables = json.dumps(data)
        self.save()

    def box_limits_top(
        self, reference_column, columns_data_top, columns_data_bot):

        vertical_limits = []
        reference_row_top = False

        for row_data in reference_column:
            if not reference_row_top:
                reference_row_top = columns_data_top
                continue

            row_top = row_data.get("vertices")[0].get("y") - 3
            vertical_limits.append({
                "top": reference_row_top,
                "bot": row_top
            })
            reference_row_top = row_top

        if reference_row_top:
            vertical_limits.append({
                "top": reference_row_top,
                "bot": columns_data_bot + 3
            })
        return vertical_limits

    def box_limits_center(
        self, reference_column, columns_data_top, columns_data_bot):

        vertical_limits = []
        linea_media = 4
        centers = []

        for row_data in reference_column:
            centers.append({
                "top": row_data.get("vertices")[0].get("y"),
                "bot": row_data.get("vertices")[2].get("y"),
                "over": False,
            })

        while not all([c["over"] for c in centers]):
            for index in range(len(centers)):
                center = centers[index]
                if center["over"]:
                    continue
                previus_center = centers[index - 1] if index > 0 else None
                next_center = centers[
                    index + 1] if index + 1 < len(centers) else None

                center["top"] -= int(linea_media / 2)
                center["bot"] += int(linea_media / 2)

                if previus_center:
                    if not previus_center["over"]:
                        previus_center["top"] -= int(linea_media / 2)
                        previus_center["bot"] += int(linea_media / 2)
                    reference_top_limit = previus_center["bot"]
                else:
                    reference_top_limit = columns_data_top
                if center["top"] <= reference_top_limit:
                    center["over"] = True
                    if previus_center:
                        previus_center["over"] = True

                if next_center:
                    if not next_center["over"]:
                        next_center["top"] -= int(linea_media / 2)
                        next_center["bot"] += int(linea_media / 2)
                    reference_bot_limit = next_center["top"]
                else:
                    reference_bot_limit = columns_data_bot
                if center["bot"] >= reference_bot_limit:
                    center["over"] = True
                    if next_center:
                        next_center["over"] = True

        for index in range(len(centers)):
            center = centers[index]
            next_center = centers[index + 1] if index + \
                1 < len(centers) else None
            if next_center:
                center_media = (center["bot"] + next_center["top"]) / 2
                center["bot"] = center_media
                next_center["top"] = center_media

            vertical_limits.append({
                "top": center["top"],
                "bot": center["bot"],
            })

        return vertical_limits

    def box_limits_bot(
        self, reference_column, columns_data_top, columns_data_bot):

        vertical_limits = []
        reference_row_top = columns_data_top

        for row_data in reference_column:
            row_bot = row_data.get("vertices")[2].get("y") + 3
            vertical_limits.append({
                "top": reference_row_top,
                "bot": row_bot
            })
            reference_row_top = row_bot

        return vertical_limits

    def get_table_data(self, recalculate=False):
        data = self.get_json_variables()

        if "table_data" in data and not recalculate:
            return data["table_data"]

        self.get_data_full_image()

        self.calculate_table_data(
            limit_position=self.public_account.vertical_align_ammounts)

        return self.get_json_variables().get("table_data") or []

    def get_blocks_in_box(self, left, right, top, bot, vision_data=False):
        # print "--------------------------"
        # print left
        # print right
        # print top
        # print bot
        # print "--------------------------"
        if not vision_data:
            vision_data = self.get_vision_data().get("full", {})
        first_opcion = False
        data = []
        for block in vision_data:
            vertices = block.get("vertices")
            y_top = vertices[0].get("y")
            y_bot = vertices[3].get("y")

            if not (y_top >= top and y_bot <= bot):
                # fuera de los limites alto y bajo

                # comprovar el porcentaje interno antes de ignorarlo
                continue

            x_left = vertices[0].get("x")
            x_right = vertices[1].get("x")

            if x_left >= left and x_right <= right:
                # bloques completos dentro de los limites

                # separar los bloques en lineas  conservando su posicion y
                lines = get_lines_in_block(block)
                data += lines
                pass
            elif (x_left >= left and x_left <= right) or (x_right >= left and x_right <= right):
                # Solo una parte del bloque esta en los limites
                """
                separarlos en lineas, y por palabras revisar quienes entran
                en el limite, las palabras recortadas deven ofrecer un ajuste
                en los limites dependiendo si porcentaje recortado es menor
                al porcentaje dentro de los limites
                """
                lines = get_lines_in_block(block)
                lines_content = []
                for line in lines:
                    line_content = content_in_limits(line, left, right)
                    if line_content:
                        lines_content.append(line_content)
                data += lines_content
                pass
            elif left >= x_left and right <= x_right:
                # el bloque atravieza por completo los limites
                """
                mismas acciones que el caso de arriba, solo una porcion
                centrica del bloque es valida
                """
                lines = get_lines_in_block(block)
                lines_content = []
                for line in lines:
                    line_content = content_in_limits(line, left, right)
                    if line_content:
                        lines_content.append(line_content)
                data += lines_content
                pass

        # reordenamiento de las filas por odern decendente en y
        def block_fy(e):
            return e['fy']
        data.sort(key=block_fy)
        # for block in data:
        #     print block.get("w")
        return data

    def get_vision_data(self):
        import json
        try:
            return json.loads(self.vision_data)
        except Exception as e:
            print e
            return {}

    def get_json_variables(self):
        import json
        try:
            return json.loads(self.json_variables)
        except Exception as e:
            print("self.json_variables No JSON object could be decoded, "
                  "se reiniciara a { }")
            return {}

    def calcColumns(self, type_col, strict=False):
        import json
        from scripts.data_cleaner import calcColumnsNumbers, calculateSuburb
        is_sub = type_col == 'suburbs'
        cut = '1' if is_sub else '2'
        scraping_values = self.get_json_variables().get(cut, {})
        if is_sub:
            column_values = calculateSuburb(scraping_values, self)
        else:
            column_values, len_array = calcColumnsNumbers(
                scraping_values, strict)
        if not strict:
            try:
                #self['data_row_%s'%type_col] = json.dumps(column_values)
                setattr(
                    self, 'data_row_%s' %
                    type_col, json.dumps(column_values))
                if not is_sub:
                    self.len_array_numbers = json.dumps(len_array)
                self.save()
            except Exception as e:
                set_new_error(
                    self,
                    "No logramos guardar columnas %s -->" %
                    type_col)
                set_new_error(self, e)
        return column_values if is_sub else (column_values, len_array)

    def comprobate_stability(
        self, all_orphan_rows, ord_numbers,
        ord_suburbs, final_compr=False, from_last=False):

        stable_row = len(ord_numbers) == len(ord_suburbs)
        if not stable_row:
            real_ord_suburbs = [x for x in ord_suburbs if x["suburb_id"]]
            if len(ord_numbers) == len(real_ord_suburbs):
                stable_row = True
                ord_suburbs = real_ord_suburbs
        # el número de columnas coincide:
        if stable_row:
            orphan_stable_subs = self.save_complete_rows(
                ord_numbers, ord_suburbs)
            all_orphan_rows["suburbs"] += orphan_stable_subs
        else:
            all_orphan_rows["numbers"] += ord_numbers
            all_orphan_rows["suburbs"] += ord_suburbs
            if final_compr:
                print ord_suburbs
                self.last_comprob_missings(ord_numbers, ord_suburbs)
            if from_last:
                print "inestable_suburbs"
                print len(ord_numbers)
                print len(ord_suburbs)
                print len(real_ord_suburbs)
                print self.path
                set_new_error(self, "La colomna de Colonia es inestable")
                self.status = "inestable_suburbs"
                self.save()
        return all_orphan_rows

    def last_comprob_missings(self, ord_numbers, ord_suburbs):
        from scripts.data_cleaner import saveFinalProjSuburb
        print u"A CONTINUACIÓN, LA LISTA DE LOS SUBS FALTANTES:"
        print u"0 --> Ninguno coincide"
        missings_subs_last = Suburb.objects.filter(
            townhall=self.public_account.townhall,
            finalproject__period_pp=self.public_account.period_pp,
            finalproject__image__isnull=True).order_by('short_name')
        for sub in missings_subs_last:
            print u"%s --> %s" % (sub.id, sub.short_name)

        missing_rows_idxs = [idx for idx, x in enumerate(ord_suburbs)
                             if not x["suburb_id"]]
        print u"---------------------------------"
        print u"ESTAS SON LAS COLUMNAS POSIBLES:"
        for miss_idx in missing_rows_idxs:
            print "%s --> %s" % (miss_idx + 1, ord_suburbs[miss_idx]['curr'])
            try:
                print "   COMB| %s" % (ord_suburbs[miss_idx]['comb'])
            except Exception as e:
                pass

        has_new_data = False
        for lap in xrange(40):
            answer_1 = input("Escribe el id de la colonia que coincide:")
            print answer_1
            if answer_1 == 0:
                break
            else:
                answer_2 = input("Escribe la columna con la que coincide:")
                if answer_2 == 0:
                    continue
                else:
                    sub_id = saveFinalProjSuburb(answer_1, self, -1)
                    if (sub_id):
                        ord_suburbs[answer_2 - 1]["suburb_id"] = sub_id
                        has_new_data = True
                    else:
                        print u"!!NO ECONTRAMOS LO QUE DESEABAS!!"
                    continue
        if has_new_data:
            for_not_error = {"suburbs": [], "numbers": []}
            self.comprobate_stability(for_not_error, ord_numbers,
                                      ord_suburbs, False, True)

    def save_complete_rows(self, ordered_numbers, ordered_suburbs):
        from pprint import pprint
        from project.models import FinalProject
        # LUCIAN: Estoy imprimiendo esto para ayudar a las pruebas
        # pprint(ordered_numbers)
        # pprint(ordered_suburbs)
        # aquí vas a tomar, en el orden en el que están y los vas a insertar
        is_complete = True
        orphan_rows = []
        has_numbers = len(ordered_numbers)
        base_for_enum = ordered_numbers if has_numbers else ordered_suburbs

        for idx, column_num in enumerate(base_for_enum):
            sub_row = ordered_suburbs[idx]
            if has_numbers:
                ordered_suburbs[idx]["number_data"] = column_num
            suburb_id = sub_row.get("suburb_id")
            if suburb_id:
                if isinstance(suburb_id, int):
                    final_proj = FinalProject.objects.filter(
                        suburb__id=suburb_id,
                        period_pp=self.public_account.period_pp).first()
                    if final_proj:
                        self.set_values_final_proj(final_proj, sub_row)
                else:
                    print "!!!!!no es de tipo int (save_complete_rows)"
                    set_new_error(
                        self,
                        u"guardamos el sub_id como '%s' (no numérico)"
                        % suburb_id)
                    final_proj = False

            else:
                final_proj = False

            if not final_proj:
                orphan_rows.append(sub_row)
                is_complete = False
                # continue

        self.data_row_suburbs = ordered_suburbs
        self.save()

        if is_complete:
            self.status = "completed"
            print "completed"
        else:
            self.status = "stable_row"
            set_new_error(self, "Hay cosas que faltan por completar")

        self.save()

        # pprint(orphan_rows)
        return orphan_rows

    def __unicode__(self):
        return u"%s %s" % (self.public_account, self.path)

    def set_values_final_proj(self, final_proj, sub_row):
        import json
        final_proj.json_variables = json.dumps(sub_row)
        for ammount in amm_types:
            curr_amm = sub_row.get("number_data", {}).get(ammount)
            if curr_amm:
                if curr_amm["correct_format"]:
                    setattr(final_proj, ammount, curr_amm.get("final_value"))
                    final_proj.inserted_data = True
                else:
                    set_new_error(final_proj, u"%s >> formato incorrecto: %s" % (
                        ammount, curr_amm.get("raw_unity")))
            else:
                set_new_error(final_proj,
                              u"%s >> No tiene ningún valor " % ammount)

            final_proj.image = self
        final_proj.save()


def append_comprob(comprobs, row, name):
    try:
        comprobs.append({"value": row[name], "name": name})
    except Exception as e:
        pass
    return comprobs


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


def formatter_orphan(all_images, all_orphan_rows):
    new_orphan_rows = {"suburbs": [], "numbers": []}
    # print all_orphan_rows
    for image in all_images:
        current_suburbs = [x for x in all_orphan_rows[
            "suburbs"] if x["image_id"] == image.id]
        current_numbers = [x for x in all_orphan_rows[
            "numbers"] if x["image_id"] == image.id]
        print "--------------------------"
        # print current_numbers
        # print current_suburbs
        # signfica que no coincidieron las columnas de ambos recortes:
        if len(current_numbers):
            print u"sí hay numbers"
            print image.path
            new_orphan_rows = image.comprobate_stability(
                new_orphan_rows, current_numbers, current_suburbs, True)
        else:
            print u"no hay numbers"
            print image.path
            orphan_stable_subs = image.save_complete_rows(
                current_numbers, current_suburbs)
            new_orphan_rows["suburbs"] += orphan_stable_subs
    return new_orphan_rows


def flexibleMatchSuburb(orphan_subs, pa):
    from scripts.data_cleaner import similar, saveFinalProjSuburb
    from pprint import pprint
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
                #comb_bigger = may == 'comb'
                #triple_bigger = may == 'triple'
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
                image, u"No se encontró el seq %s para ponerlo como ínválido")
            print e
    return orphan_subs


def get_lines_in_block(block):
    lines = []
    line = []
    for paragraph in block.get("block", {}).get("paragraphs", []):
        for word in paragraph.get("words", []):
            vertices = word.get("vertices")
            line.append(word)
            detected_break = word.get("detected_break")
            if detected_break in [3, 4, 5]:
                full_line = u" ".join([w.get("word") for w in line])
                """
                se espera que sea una sola linea, por lo que sus vertices
                deverian ser  los 0 y 3 del primer bloque y 1 y2 del
                ultimo  bloque
                """
                first_vertices = line[0].get("vertices")
                final_vertices = [
                    first_vertices[0],
                    vertices[1],
                    vertices[2],
                    first_vertices[3],
                ]
                lines.append({
                    "w": full_line,
                    "fy": final_vertices[0].get("y", 0),
                    "words": line,
                    "detected_break": detected_break,
                    "vertices": final_vertices
                })
                line = []
    return lines


def content_in_limits(line, left, right):
    line_content = []
    if not line:
        return False
    for word in line.get("words"):
        vertices = word.get("vertices")
        x_left = vertices[0].get("x")
        x_right = vertices[1].get("x")

        if x_left >= left and x_right <= right:
            # palabra completos dentro de los limites
            line_content.append(word)
            continue

        full = x_right - x_left
        if (x_left >= left and x_left <= right):
            # porcion izquierda
            fraccion = right - x_left
        elif(x_right >= left and x_right <= right):
            # porcion derecha
            fraccion = x_right - left
        elif left >= x_left and right <= x_right:
            # la palabra atravieza los limites, se deve contemplar?
            line_content.append(word)
            continue
        else:
            continue
        porcentaje = (fraccion * 100) / full
        if porcentaje > 70:
            line_content.append(word)

    if line_content:
        full_line = u" ".join([w.get("word") for w in line_content])
        # usar el detected_break de contenido o de la linea original?
        detected_break = line.get("words")[-1].get("detected_break")
        first_vertices = line_content[0].get("vertices")
        last_vertices = line_content[-1].get("vertices")
        final_vertices = [
            first_vertices[0],
            last_vertices[1],
            last_vertices[2],
            first_vertices[3],
        ]
        return {
            "w": full_line,
            "fy": final_vertices[0].get("y", 0),
            "words": line_content,
            "detected_break": detected_break,
            "vertices": final_vertices
        }
    else:
        return False
