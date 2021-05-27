# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json


class PPImageReferencesMix:

    # calculo de referencias
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

    # Referencias manuales
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
