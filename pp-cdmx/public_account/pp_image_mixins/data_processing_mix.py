# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json


class PPImageDataProcessingMix:

    """-----------------------------------------------------------------------
        se espera que en este punto ya se tenga calculado la primera vercion
        de los datos por cada columna, los bloque internos estan limitados a
        una linea, siedo los mas reelevantes las ultimas 5 columnas, quienes
        mayormente tendran tendran una sola alineacion horizontal entre ellas,
        para los casos especiales, un usuario devera indicarlo manualmente en
        el admin, solo dejar las columnas mas uniformes etre si

        self.public_account.ignore_columns
    -----------------------------------------------------------------------"""

    # procesamiento de columns_data

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

    def box_limits_top(self, *args):
        reference_column, columns_data_top, columns_data_bot = args
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

    def box_limits_center(self, *args):
        reference_column, columns_data_top, columns_data_bot = args
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

    def box_limits_bot(self, *args):
        reference_column, columns_data_top, columns_data_bot = args
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
