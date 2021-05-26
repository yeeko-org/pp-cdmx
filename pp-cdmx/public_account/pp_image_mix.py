# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from geographic.models import Suburb

from scripts.data_cleaner import set_new_error

amm_types = ["progress", "approved", "modified", "executed", "variation"]


class PPImageDataProcessingMix:

    def get_table_ref(self):
        try:
            return json.loads(self.table_ref)
        except Exception:
            return []

    def set_table_ref(self, data):
        try:
            self.table_ref = json.dumps(data)
        except Exception:
            self.table_ref = None

    def calculate_table_ref_columns(self):
        manual_ref = self.get_manual_ref()
        table_ref_columns = None
        if manual_ref:
            table_ref_columns = [manual_ref.get("right")]
            table_ref_columns += manual_ref.get("divisors")
            table_ref_columns += [manual_ref.get("left")]
        else:
            data = self.get_json_variables()
            columns_boxs = data.get("columns_boxs")
            if isinstance(columns_boxs, list) and columns_boxs:
                first_column = columns_boxs[0]
                table_ref_columns = [first_column.get("left", 0)]
                for column in columns_boxs:
                    table_ref_columns.append(column.get("right", 0))

        if table_ref_columns:
            self.table_ref_columns = json.dumps(table_ref_columns)
            self.save()

    # revicion de referencias ------------------------------------------------

    # evaluacion manual de los headers, para marcar cuales fueron erroneos,
    # esto puede ser por año solo para las paginas 1

    # La imagen 2019 -- IZP PP-2019-IZP_0001.png 430 no proceso Table Data

    def is_first_page(self):
        if "0001" in self.path:
            return True
        return False

    def valid_headers(self):
        try:
            headers = json.loads(self.headers)
        except Exception:
            return False
        valid_header = False
        if len(headers) == 8:
            valid_header = all(headers)
        return valid_header

    def need_manual_ref_calculate(self):
        data = self.get_json_variables()
        need_manual_ref = False
        data_left = data.get("data_left")

        valid_header = self.valid_headers()

        if self.is_first_page():
            title_rigth = data.get("title_rigth")
            logo_left = data.get("logo_left")
            if not title_rigth or not logo_left:
                need_manual_ref = True
            if not data_left or not valid_header:
                need_manual_ref = True
        else:
            if not data_left or not valid_header:
                title_rigth = data.get("title_rigth")
                logo_left = data.get("logo_left")
                if not title_rigth or not logo_left:
                    need_manual_ref = True
        self.need_manual_ref = need_manual_ref
        self.save()

        if need_manual_ref:
            print self

    # ------------------------------------------------------------------------

    @property
    def period(self):
        return self.public_account.period_pp

    def reset(self):
        self.json_variables = None
        self.save()

    def get_first_image(self):
        from public_account.models import PPImage
        if self.is_first_page():
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
        # self.cleand_columns_numbers()

    def find_block(
            self, text=False, regex=False, full_obj=False, lines=False,
            single_word=False, allow_single_word=False,
            similar_value_min=0.7, show_options=False, many_options=False):
        from scripts.data_cleaner import similar
        import re

        def block_value(e):
            return e['similar_value']

        if text:
            if u";" in text:
                options = []
                for option_text in text.split(";"):
                    block_option = self.find_block(
                        option_text.strip(),
                        single_word=single_word,
                        allow_single_word=allow_single_word,
                        similar_value_min=similar_value_min,
                        show_options=show_options)
                    if block_option:
                        options.append(block_option)
                if options:
                    options.sort(key=block_value)
                    if many_options:
                        options.reverse()
                        return options
                    return options[-1]
                else:
                    return False

        vision_data = self.get_vision_data().get("full", {})
        # first_opcion = False
        opcion = []
        for block in vision_data:
            complete_w = block.get("w", "")
            block_x = block.get("vertices")[0].get("x")
            block_y = block.get("vertices")[0].get("y")
            var_posit = float(block_x + block_y) / 1000000

            if text:
                # from pprint import pprint
                # if text.lower() in complete_w.lower():
                #     pprint(complete_w)
                if lines:
                    for line in complete_w.split("\n"):
                        similar_value = similar(text.lower().strip(),
                                                line.lower().strip())
                        if similar_value > similar_value_min:
                            opcion.append(
                                {
                                    "block": block,
                                    "similar_value": similar_value - var_posit
                                }
                            )

                elif single_word:
                    """
                    nueva variante, esta se presenta como ultimo recurso,
                    busqueda de una sola palabra en el bloque, para los casos
                    en que las cabezeras se mezclen en un solo bloque
                    """
                    best_word_opcion = False
                    similar_value = 0
                    for paragraph in block.get("block").get("paragraphs"):
                        for word in paragraph.get("words"):
                            word_text = word.get("word")
                            similar_value = similar(
                                text.lower().strip(),
                                word_text.lower().strip())

                            if similar_value > 0.8:
                                word["w"] = word_text
                                best_word_opcion = word
                                break
                        if best_word_opcion:
                            break

                    if best_word_opcion:
                        opcion.append(
                            {
                                "block": best_word_opcion,
                                "similar_value": similar_value - var_posit
                            }
                        )
                        break

                else:
                    similar_value = similar(text.lower().strip(),
                                            complete_w.lower().strip())
                if similar_value > similar_value_min:
                    opcion.append(
                        {
                            "block": block,
                            "similar_value": similar_value - var_posit
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
                            "similar_value": 1 - var_posit
                        }
                    )

        if not opcion:
            if not single_word and text and allow_single_word:
                """
                si el bloque a buscar es de una sola palabra,se puede
                intentar buscar por palabras en los bloques, siempre y cuando
                la busqueda actual no sea por busqueda de una sola palabra
                single_word y se permita la busqueda por single_word
                """
                words = [word.strip() for word in text.split(" ") if word]
                if len(words) == 1:
                    return self.find_block(
                        text=words[0], single_word=True,
                        similar_value_min=similar_value_min,
                        show_options=show_options, many_options=many_options)
            return False

        opcion.sort(key=block_value)
        if show_options:
            for o in opcion:
                w = o.get("block").get("w")
                value = o.get("similar_value")
                print w
                print value
                print

        if many_options:
            opcion.reverse()
            return [
                {
                    "vertices": op.get("block").get("vertices"),
                    "w": op.get("block").get("w"),
                    "similar_value": op.get("similar_value")
                }
                for op in opcion]

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

    def find_reference_blocks(self, show_options=False):
        self.find_block_logo(show_options=show_options)
        self.find_block_unidad(show_options=show_options)
        self.find_block_title(show_options=show_options)
        self.find_block_ppd(show_options=show_options)
        self.find_block_ammounts(show_options=show_options)
        self.find_headers(show_options=show_options)

    def check_reference(self):
        data = self.get_json_variables()
        # columns_headers = data.get("columns_headers")
        columns_headers = self.get_headers()
        if not isinstance(columns_headers, list):
            columns_headers = []

        reference = {
            "logo": True if data.get("logo_left") else False,
            "unidad": True if data.get("unidad_bot") else False,
            "title": True if data.get("title_rigth") else False,
            "ppd": True if data.get("data_center") else False,
            "ammounts": True if data.get("ammounts_center") else False,
        }
        try:
            reference["colonia"] = True if columns_headers[0] else False
        except Exception:
            reference["colonia"] = False
        try:
            reference["proyecto"] = True if columns_headers[1] else False
        except Exception:
            reference["proyecto"] = False
        try:
            reference["descripcion"] = True if columns_headers[2] else False
        except Exception:
            reference["descripcion"] = False
        try:
            reference["avance"] = True if columns_headers[3] else False
        except Exception:
            reference["avance"] = False
        try:
            reference["aprobado"] = True if columns_headers[4] else False
        except Exception:
            reference["aprobado"] = False
        try:
            reference["modificado"] = True if columns_headers[5] else False
        except Exception:
            reference["modificado"] = False
        try:
            reference["ejercido"] = True if columns_headers[6] else False
        except Exception:
            reference["ejercido"] = False
        try:
            reference["variacion"] = True if columns_headers[7] else False
        except Exception:
            reference["variacion"] = False

        return reference

    def find_block_logo(self, show_options=False):
        block_logo = self.find_block(
            self.period.logo or "gobierno de la ciudad de mexico",
            show_options=show_options)

        if not block_logo:
            return
        vertices = block_logo.get("vertices")
        data = self.get_json_variables()
        # data["logo"] = first_opcion

        data["logo_left"] = vertices[0].get("x")
        data["logo_bot"] = vertices[3].get("y")
        self.json_variables = json.dumps(data)
        self.save()

    def find_block_unidad(self, show_options=False):
        block_unidad = self.find_block(
            (self.period.unidad or u"unidad responsable del gasto: ") +
            self.public_account.townhall.name,
            show_options=show_options)
        if not block_unidad:
            block_unidad = self.find_block(
                self.period.unidad or u"unidad responsable del gasto",
                show_options=show_options)
        if not block_unidad:
            # considerar otras medidas como variantes
            return
        data = self.get_json_variables()
        data["unidad_bot"] = block_unidad.get("vertices")[3].get("y")
        data["data_left"] = block_unidad.get("vertices")[0].get("x")
        self.json_variables = json.dumps(data)
        self.save()

    def find_block_title(self, show_options=False):
        block_title = self.find_block(
            self.period.title or
            ("cuenta publica de la ciudad de mexico %s" % self.period.year),
            show_options=show_options)
        if not block_title:
            # considerar otras medidas como variantes
            return
        data = self.get_json_variables()
        # data["block_title"] = block_title
        data["title_rigth"] = block_title.get("vertices")[1].get("x")
        self.json_variables = json.dumps(data)
        self.save()

    def find_block_ppd(self, show_options=False):
        block_ppd = self.find_block(
            self.period.ppd or
            "ppd presupuesto participativo para las delegaciones",
            show_options=show_options)
        if not block_ppd:
            # considerar otras medidas como variantes
            return
        data = self.get_json_variables()
        # data["block_ppd"] = block_ppd

        block_ppd_rigth = block_ppd.get("vertices")[1].get("x")
        block_ppd_left = block_ppd.get("vertices")[0].get("x")
        data["data_center"] = (block_ppd_rigth + block_ppd_left) / 2
        self.json_variables = json.dumps(data)
        self.save()

    def find_block_ammounts(self, show_options=False):
        block_ammounts = self.find_block(
            self.period.ammounts or "presupuesto (pesos con dos decimales",
            show_options=show_options)
        if not block_ammounts:
            # considerar otras medidas como variantes
            return
        data = self.get_json_variables()
        # data["block_ammounts"] = block_ammounts

        block_ammounts_rigth = block_ammounts.get("vertices")[1].get("x")
        block_ammounts_left = block_ammounts.get("vertices")[0].get("x")
        data["ammounts_center"] = (
            block_ammounts_rigth + block_ammounts_left) / 2
        self.json_variables = json.dumps(data)
        self.save()

    def find_headers(self, show_options=False, return_result=False):
        import re
        colonia = self.find_block(
            self.period.colonia or u"colonia o pueblo originario",
            show_options=show_options, many_options=True)
        proyecto = self.find_block(
            self.period.proyecto or u"proyecto",
            show_options=show_options, many_options=True)
        descripcion = self.find_block(
            self.period.descripcion or u"descripción",
            show_options=show_options, many_options=True)
        avance = self.find_block(
            self.period.avance or u"avance del proyecto",
            show_options=show_options, many_options=True)
        if not avance:
            avance = self.find_block(
                regex=r'Proyecto(?:$|\s\S+)?',
                show_options=show_options, many_options=True)

        aprobado = self.find_block(
            self.period.aprobado or u"aprobado", allow_single_word=True,
            show_options=show_options, many_options=True)
        # --------------------------------------------------------------------
        # ajuste de ancho en aprovacion
        if aprobado:
            if not isinstance(aprobado, list):
                aprobado = [aprobado]
            for sub_aprobado in aprobado:
                if not isinstance(sub_aprobado, dict):
                    print sub_aprobado
                    continue
                text_aprobado = sub_aprobado.get("w")
                if text_aprobado:
                    # se espera un asterisco obligatorio despues de Aprobado
                    x = re.search(r'Aprobado( )*(\*)', text_aprobado)
                    # print text_aprobado
                    if not x:
                        # print "se le agrego variacion de 10 pixeles"
                        vertices = sub_aprobado.get("vertices")
                        p1 = vertices[1]
                        p2 = vertices[2]
                        p1["x"] = p1["x"] + 10
                        p2["x"] = p2["x"] + 10
                        sub_aprobado["vertices"] = [vertices[0], p1,
                                                    p2, vertices[3]]
                    # else:
                    #     print "no se le agrego variacion"
                    # print
        # --------------------------------------------------------------------
        modificado = self.find_block(
            self.period.modificado or u"modificado", allow_single_word=True,
            show_options=show_options, many_options=True)
        ejercido = self.find_block(
            self.period.ejercido or u"ejercido", allow_single_word=True,
            show_options=show_options, many_options=True)
        variacion = self.find_block(
            self.period.variacion or u"variación", allow_single_word=True,
            show_options=show_options, many_options=True)
        # --------------------------------------------------------------------
        # ajuste de ancho en variacion
        if variacion:
            if not isinstance(variacion, list):
                variacion = [variacion]
            for sub_variacion in variacion:
                if not isinstance(sub_variacion, dict):
                    print sub_variacion
                    continue
                text_variacion = sub_variacion.get("w").strip()
                if text_variacion:
                    # el porciento puede ser con salto de linea
                    x = re.search(r'Variación(\s)*(%|\$)', text_variacion)
                    # print text_variacion
                    if not x:
                        # print "se le agrego variacion de 20 pixeles"
                        vertices = sub_variacion.get("vertices")
                        p1 = vertices[1]
                        p2 = vertices[2]
                        p1["x"] = p1["x"] + 20
                        p2["x"] = p2["x"] + 20
                        sub_variacion["vertices"] = [vertices[0], p1,
                                                     p2, vertices[3]]
                    # else:
                    #     print "no se le agrego variacion"
                    # print
        # --------------------------------------------------------------------

        columns_headers = [
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

        self.headers = json.dumps(columns_headers)
        self.save()

        if return_result:
            return columns_headers

    def get_headers(self, reset=True, show_options=False, show_prints=False):
        # se revisa si ya se tiene o si se puede calcular los headers
        if reset:
            self.headers = None
        try:
            columns_headers = json.loads(self.headers)
        except Exception:
            columns_headers = None

        # calculando los headers si no se encuentran
        if not columns_headers:
            self.find_headers(show_options=show_options)

        try:
            columns_headers = json.loads(self.headers)
        except Exception:
            columns_headers = None

        revised_columns_headers = check_columns_headers(
            columns_headers, show_prints=show_prints)

        data = self.get_json_variables()
        data_left = data.get("data_left")

        # calcular las columnas de la pagina 0001
        is_path_0001 = "0001" not in self.path
        if (not revised_columns_headers or not data_left) and is_path_0001:

            first_image = self.get_first_image()
            first_image_data = first_image.get_json_variables()
            first_data_left = first_image_data.get("data_left")
            if not first_data_left:
                print u"        No se tiene calculado el data_left en 0001"
                return None

            first_revised_columns_headers = first_image\
                .get_headers(show_prints=show_prints)
            if not first_revised_columns_headers:
                print u"        No se tiene calculado columns_headers en 0001"
                return None

            first_logo_left = first_image_data.get("logo_left")
            first_title_rigth = first_image_data.get("title_rigth")
            if not first_logo_left or not first_title_rigth:
                print u"        Se requiere logo y titulo en %s " % first_image
                return None

            logo_left = data.get("logo_left")
            title_rigth = data.get("title_rigth")
            if not logo_left or not title_rigth:
                print u"        Se requiere logo y titulo en %s " % self
                return None

            full_first = first_title_rigth - first_logo_left
            full = title_rigth - logo_left

            dimension_percentage = float(full) / float(full_first)
            desfase = first_logo_left - int(
                float(logo_left) / dimension_percentage)

            def cross_dimensions(dimension):
                return int((dimension - desfase) * dimension_percentage)

            # revisar si existe data_left o calculala con first_image_data
            if not data_left:
                print u"        no se encontro data_left, se usara el de 0001"
                data_left = cross_dimensions(first_data_left)
                data["data_left"] = data_left
                self.json_variables = json.dumps(data)

            if not revised_columns_headers:
                print u"     inconsistencia en headers, se usaran los de 0001"
                revised_columns_headers = []
                for ref_header in first_revised_columns_headers:
                    ref_vertices = ref_header.get("vertices")

                    x_left = cross_dimensions(ref_vertices[0].get("x"))
                    x_right = cross_dimensions(ref_vertices[1].get("x"))

                    revised_columns_headers.append(
                        {"vertices": [
                            {"x": x_left},
                            {"x": x_right},
                            {"x": x_right}]}
                    )

                self.first_headers_used = True
            self.save()

        if not revised_columns_headers:
            print "        No se pudo calcular columns_headers"

        return revised_columns_headers

    def calculate_column_boxs(self, reset=True):
        # columns_headers = data.get("columns_headers", [])
        columns_headers = self.get_headers(reset=reset)
        if not columns_headers:
            print "        No se pudo obtener las cabezeras propias o de 0001"
            return

        data = self.get_json_variables()
        data_left = data.get("data_left")
        data_right = 0
        if not data_left:
            print "        No se pudo obtener data_left propio o de 0001"
            return

        columns_top = 0
        if data.get("logo_bot"):
            columns_top = data.get("logo_bot")
        if data.get("unidad_bot"):
            columns_top = data.get("unidad_bot")

        columns_boxs = []
        for header in columns_headers:

            vertices = header.get("vertices")
            center = (vertices[0].get("x") + vertices[1].get("x")) / 2
            # center=(vertices[0].get("x") + vertices[1].get("x")
            #     + vertices[2].get("x") + vertices[3].get("x"))/4

            radio = center - data_left
            data_right = center + radio

            columns_boxs.append({
                "left": data_left,
                "center": center,
                "right": data_right
            })

            data_left = data_right
            if len(vertices) > 2:
                header_bot = vertices[2].get("y")
                if header_bot > columns_top:
                    columns_top = header_bot

        if len(columns_headers) == 7:
            # la ultima cabezera no fue identificada correctamente, pero se
            # considero valido para las cabezeras porque se puede
            # calcular artificialmente

            # se calcula como el ultimo data_right
            data_left = data_right
            try:
                data = self.get_json_variables()
                data_center = data.get("data_center")
                data_left = data.get("data_left")
                data_right = (data_center - data_left) + data_center
            except Exception:
                data_right = 2200
            center = int((data_left + data_right) / 2)

            columns_boxs.append({
                "left": data_left,
                "center": center,
                "right": data_right
            })

        data["columns_boxs"] = columns_boxs
        data["columns_top"] = columns_top
        self.json_variables = json.dumps(data)
        self.save()

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
        # block_elaboro_re = self.find_block(
        #     regex=r'(REFIERE|REMANENTE|AUTORI|ELABOR|LABORADO|DIRECTOR)')
        # columns_bot = compare_block_bot(columns_bot, block_elaboro_re)

        block_autorizo = self.find_block("Autorizo :", lines=True)
        columns_bot = compare_block_bot(columns_bot, block_autorizo, 0.8)

        # busqueda de la palabra total
        block_total_urg = self.find_block("total urg")
        columns_bot = compare_block_bot(columns_bot, block_total_urg, 0.8)

        block_redondeo = self.find_block("diferencia por redondeo")
        columns_bot = compare_block_bot(columns_bot, block_redondeo, 0.8)

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
        columns_boxs = data.get("columns_boxs", [])
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

    def get_manual_ref(self):
        try:
            manual_ref = json.loads(self.manual_ref)
        except Exception as e:
            print e
            return
        references = manual_ref.get("references", )
        try:
            ref_0 = references[0]
            ref_1 = references[1]
        except Exception as e:
            print e
            return

        try:
            x0 = ref_0.get("x", 0)
            x1 = ref_1.get("x", 0)
            y0 = ref_0.get("y", 0)
            y1 = ref_1.get("y", 0)
        except Exception as e:
            print e
            return

        columns_top = y0 if y0 < y1 else y1
        columns_bot = y0 if y0 > y1 else y1
        left = x0 if x0 < x1 else x1
        right = x0 if x0 > x1 else x1

        if self.is_first_page():
            divisors = manual_ref.get("divisors")
            try:
                divisors = [divisor.get("x") for divisor in divisors]
            except Exception as e:
                print e
                return
        else:
            first_image = self.get_first_image()
            first_manual_ref_dict = first_image.get_manual_ref()
            if not first_manual_ref_dict:
                return

            first_left = first_manual_ref_dict.get("left")
            first_right = first_manual_ref_dict.get("right")
            first_divisors = first_manual_ref_dict.get("divisors")
            full_first = first_right - first_left
            full = right - left
            dimension_percentage = float(full) / float(full_first)
            desfase = first_left - int(
                float(left) / dimension_percentage)

            def cross_dimensions(dimension):
                return int((dimension - desfase) * dimension_percentage)

            divisors = []
            for divisor in first_divisors:
                divisors.append(cross_dimensions(divisor))

        if len(divisors) != 7:
            return
        divisors.sort()

        return {
            "columns_top": columns_top,
            "columns_bot": columns_bot,
            "left": left,
            "right": right,
            "divisors": divisors,
        }

    def get_data_from_columns_mr(self):
        manual_ref = self.get_manual_ref()
        if not manual_ref:
            return

        columns_top = manual_ref.get("columns_top")
        columns_bot = manual_ref.get("columns_bot")
        left = manual_ref.get("left")
        right = manual_ref.get("right")
        divisors = manual_ref.get("divisors")
        divisors.append(right)

        columns_data = []
        for divisor in divisors:
            right = divisor
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
            left = divisor
        data = self.get_json_variables()
        data["columns_data"] = columns_data
        data["columns_data_top"] = columns_top
        data["columns_data_bot"] = columns_bot

        self.json_variables = json.dumps(data)
        self.save()

    def cleand_columns_numbers(self):
        from scripts.data_cleaner import similar
        import re
        data = self.get_json_variables()
        columns_data = data["columns_data"]
        # invalids_values = ["1", "2", "3", "3/1"]
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
                column_data.pop(0)

        data["columns_data"] = columns_data
        self.json_variables = json.dumps(data)
        self.save()

    """-----------------------------------------------------------------------
        se espera que en este punto ya se tenga calculado la primera vercion
        de los datos por cada columna, los bloque internos estan limitados a
        una linea, siedo los mas reelevantes las ultimas 5 columnas, quienes
        mayormente tendran tendran una sola alineacion horizontal entre ellas,
        para los casos especiales, un usuario devera indicarlo manualmente en
        el admin, solo dejar las columnas mas uniformes etre si

        self.public_account.ignore_columns
    -----------------------------------------------------------------------"""

    def calculate_reference_column(self, columns_data_top, columns_data_bot):
        """
        Usando todos los numero disponibles dentro de los limites
        columns_data_top y columns_data_bot con magen de error de 20px
        se tomaran en cuenta todos los bloques de numeros, omitiendo los que
        se traslapen.

        en un ambiente optimo, la primera columna llenara todos los huecos y
        las demas columnas se omitiran por traslape, pero si se tiene perdida
        de datos, las filas que falten se llenaran con las demas columnas,
        cuando no se encuentre traslape.
        """
        columns_data_top -= 20
        columns_data_bot += 20
        data = self.get_json_variables()
        columns_data = data["columns_data"]
        reference_column = []
        ignore_columns = self.public_account.ignore_columns or ""
        for index in range(3, 8):
            if "%s" % (index + 1) in ignore_columns:
                continue
            for block in columns_data[index]:

                block_vertices = block.get("vertices")
                b_top = block_vertices[0].get("y")
                b_bot = block_vertices[2].get("y")
                if not (b_top > columns_data_top and
                        b_bot < columns_data_bot):
                    continue

                overlap = False
                for ref_block in reference_column:
                    # revisar si se traslapa con el presente, si es asi,
                    # continuar
                    ref_block_vertices = ref_block.get("vertices")
                    rb_top = ref_block_vertices[0].get("y")
                    rb_bot = ref_block_vertices[2].get("y")

                    over_ref = b_top < rb_top and b_bot < rb_top
                    below_ref = b_top > rb_bot and b_bot > rb_bot

                    if not (over_ref or below_ref):
                        overlap = True
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
        # normal_counts = sorted([key for key,
        # value in columns_counts.items()])
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
        if not columns_data:
            return
        try:
            row_0_y = columns_data[0][0].get("vertices")[0].get("y")
        except Exception:
            return
        try:
            row_1_y = columns_data[1][0].get("vertices")[0].get("y")
        except Exception:
            row_1_y = row_0_y
        try:
            row_2_y = columns_data[2][0].get("vertices")[0].get("y")
        except Exception:
            row_2_y = row_1_y

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
        if not columns_data:
            return

        try:
            row_0_y = columns_data[0][-1].get("vertices")[2].get("y")
        except Exception:
            return
        try:
            row_1_y = columns_data[1][-1].get("vertices")[2].get("y")
        except Exception:
            row_1_y = row_0_y
        try:
            row_2_y = columns_data[2][-1].get("vertices")[2].get("y")
        except Exception:
            row_2_y = row_1_y

        # el limite superior de el dato mas alto con un ajuste de -5 pixeles
        row_x_y = row_0_y if row_0_y > row_1_y else row_1_y
        data["columns_data_bot"] = row_x_y if row_x_y > row_2_y else row_2_y
        data["columns_data_bot"] += 5
        self.json_variables = json.dumps(data)
        self.save()
        return data["columns_data_bot"]

    def calculate_table_data(self, limit_position=None):
        from public_account.models import Row
        # cambio de logica para objetos Row
        data = self.get_json_variables()
        columns_data = data.get("columns_data")
        if not columns_data:
            print u"        No se tiene columns_data"
            return
        if not limit_position:
            limit_position = self.public_account.vertical_align_ammounts
        # if not all(data["columns_data"]):
        #     print u"        Se esperava 8 columnas, todas con datos"
        #     return
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

        table_data = []
        sequential = 0
        for vertical_limit in vertical_limits:
            row_top = vertical_limit.get("top")
            row_bot = vertical_limit.get("bot")
            row_data = []  # fragmentos unidos en los datos finales
            row_blocks = []  # informacion de vision
            for column_data in columns_data:
                cell_blocks = []
                for block in column_data:
                    vertices = block.get("vertices")
                    block_top = vertices[0].get("y")
                    block_bot = vertices[3].get("y")
                    if block_top >= row_top and block_bot <= row_bot:
                        # palabra completos dentro de los limites
                        cell_blocks.append(block)
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
                        cell_blocks.append(block)
                        continue
                    else:
                        continue
                    porcentaje = (fraccion * 100) / full
                    if porcentaje > 60:
                        cell_blocks.append(block)
                """
                En este punto tenemos una nuve ordenada de menor a mayor en y
                de lineas
                la primera accion fue concatenarlas en ese orden, suegiendo
                un problema, algunas veces una sola linea visual tiene
                una inclinacion que con mucha separa cion forma bloque
                de lineas separadas en desorden
                [linea 1 y:200] [linea 2 y:195] [linea 3 y:196]
                [linea 4 y:220]
                [linea 5 y:240]
                resultando en  "linea 2 linea 3 linea 1 linea 4 linea 5"
                solucion:
                agrupar las lineas en potenciales lineas mas grandes,
                ordenando los subgrupos por su pocicion en x
                """
                lines_goup = []
                for line in cell_blocks:
                    vertices = line.get("vertices")
                    line["fx"] = vertices[0]["x"]
                    lyt = vertices[0]["y"]
                    lyb = vertices[2]["y"]
                    add_lg = False
                    for lg in lines_goup:
                        if lyt > (lg["yt"]) and lyb < (lg["yb"]):
                            lg["lines"].append(line)
                            add_lg = True
                            continue
                    if add_lg:
                        continue
                    margen = float(lyb - lyt) * 0.3
                    new_lines_goup = {
                        "yt": vertices[0]["y"] - margen,
                        "yb": vertices[2]["y"] + margen,
                        "lines": [line]
                    }
                    lines_goup.append(new_lines_goup)

                def block_fx(e):
                    return e['fx']
                final_lines = []
                for line_goup in lines_goup:
                    lines = line_goup["lines"]
                    lines.sort(key=block_fx)
                    final_lines.append(" ".join(
                        [line.get("w") for line in lines]))
                line_text = u" ".join(
                    [line for line in final_lines])
                line_text = line_text.replace(u"\n", " ").strip()
                row_data.append(line_text)
                row_blocks.append(cell_blocks)

            # creacion del nuevo objeto Row con la informacion generada
            row_obj, is_created = Row.objects.get_or_create(
                image=self, sequential=sequential)
            row_obj.vision_blocks = json.dumps(row_blocks)
            row_obj.vision_data = json.dumps(row_data)
            row_obj.vision_data = json.dumps(row_data)
            row_obj.top = row_top
            row_obj.bottom = row_bot
            row_obj.save()
            table_data.append(row_data)
            sequential += 1

        # data["table_data"] = table_data
        # self.json_variables = json.dumps(data)
        # from pprint import pprint
        # pprint (table_data)
        self.set_table_ref(vertical_limits)
        self.table_data = json.dumps(table_data)
        self.save()

    def calculate_table_ref(self, limit_position="top"):
        data = self.get_json_variables()
        columns_data = data.get("columns_data")
        if not columns_data:
            print u"        No se tiene columns_data"
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
        self.set_table_ref(vertical_limits)
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
        # cambio de logica a creacion de registro de objetos Row por ppimage
        try:
            table_data = json.loads(self.table_data)
        except Exception:
            table_data = None

        if table_data and not recalculate:
            return table_data

        self.get_data_full_image()

        self.calculate_table_data(
            limit_position=self.public_account.vertical_align_ammounts)

        try:
            return json.loads(self.table_data)
        except Exception:
            return []

    def get_blocks_in_box(self, left, right, top, bot, vision_data=False):
        # print "--------------------------"
        # print left
        # print right
        # print top
        # print bot
        # print "--------------------------"
        if not vision_data:
            vision_data = self.get_vision_data().get("full", {})
        # first_opcion = False
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
            elif ((x_left >= left and x_left <= right) or
                  (x_right >= left and x_right <= right)):
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
        if hasattr(self, "_vision_data"):
            return self._vision_data
        import json
        try:
            self._vision_data = json.loads(self.vision_data)
        except Exception as e:
            print e
            self._vision_data = {}
        return self._vision_data

    def get_json_variables(self):
        import json
        try:
            return json.loads(self.json_variables)
        except Exception:
            # print("self.json_variables No JSON object could be decoded, "
            #       "se reiniciara a { }")
            return {}

    def calc_columns(self, type_col, strict=False):
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
                # self['data_row_%s'%type_col] = json.dumps(column_values)
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
            except Exception:
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
        # from pprint import pprint
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
                    set_new_error(
                        final_proj,
                        u"%s >> formato incorrecto: %s" % (
                            ammount, curr_amm.get("raw_unity")))
            else:
                set_new_error(final_proj,
                              u"%s >> No tiene ningún valor " % ammount)

            final_proj.image = self
        final_proj.save()


def check_columns_headers(columns_headers, show_prints=False):
    no_headers = 8
    if not isinstance(columns_headers, list):
        if show_prints:
            print u"        columns_headers no es una lista"
        return

    elif not len(columns_headers) == 8:
        if show_prints:
            print u"        Se esperava una lista de 8 elementos"
            print u"        Actualemnte tiene: %s" % len(columns_headers)
        return

    elif not all(columns_headers):
        # si la cabezera faltante es la ultima, se puede considerar valido
        no_headers = 7
        if not all(columns_headers[:7]):
            if show_prints:
                print u"    El find_headers no encontro todas las cabezeras"
            return

    previus_block = 0
    revised_columns_headers = []
    for header in columns_headers[:no_headers]:
        revised_header = False
        center = 0
        if isinstance(header, list):
            for sub_header in header:
                if not isinstance(sub_header, dict):
                    print sub_header
                    continue
                vertices = sub_header.get("vertices")
                center = (vertices[0].get("x") + vertices[1].get("x")) / 2
                if center < previus_block:
                    continue
                revised_header = sub_header
                break
        else:
            vertices = header.get("vertices")
            center = (vertices[0].get("x") + vertices[1].get("x")) / 2
            if not (center < previus_block):
                revised_header = header

        if not revised_header:
            if show_prints:
                print "****************************************************"
                print u"        inconsistencia de las cabezeras"
                print u"        Requiere revicion manual"
                print "****************************************************"
            return
        previus_block = center
        revised_columns_headers.append(revised_header)
    return revised_columns_headers


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
