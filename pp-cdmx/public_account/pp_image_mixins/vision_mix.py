# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json


class PPImageVisionMix:

    # Vision
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

    def calculate_table_ref_columns(self):
        manual_ref = self.get_manual_ref()
        table_ref_columns = None
        if manual_ref:
            table_ref_columns = [manual_ref.get("left")]
            table_ref_columns += manual_ref.get("divisors")
            table_ref_columns += [manual_ref.get("right")]
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

    def valid_headers(self):
        try:
            headers = json.loads(self.headers)
        except Exception:
            return False
        valid_header = False
        if len(headers) == 8:
            valid_header = all(headers)
        return valid_header

    def get_data_full_image(self):
        self.find_reference_blocks()
        self.calculate_columns_bot()
        self.calculate_column_boxs()
        self.get_data_from_columns()
        # self.cleand_columns_numbers()

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

    def find_block(self, *args, **kwargs):

        text = kwargs.get("text", False)
        regex = kwargs.get("regex", False)
        full_obj = kwargs.get("full_obj", False)
        lines = kwargs.get("lines", False)
        single_word = kwargs.get("single_word", False)
        allow_single_word = kwargs.get("allow_single_word", False)
        similar_value_min = kwargs.get("similar_value_min", 0.7)
        show_options = kwargs.get("show_options", False)
        many_options = kwargs.get("many_options", False)

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
