# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import re

from scripts.data_cleaner import set_new_error
from scripts.data_cleaner_v2 import calculateNumber


class PublicAccountCleanerMix:

    # cleaning
    def column_formatter_v3(self, reset=False, image_num=None):
        from public_account.models import PPImage, Row
        print
        print
        print "----Cuenta publica %s, id: %s----" % (self, self.id)
        # from scripts.data_cleaner_v3 import (
        #     get_normal_name,
        #     clean_text,
        #     calculate_special_formats_v3)
        # import numpy
        # suburbs_dict = []

        all_images = PPImage.objects.filter(public_account=self)
        if image_num:
            all_images = all_images.filter(path__icontains=image_num)

        if reset:
            self.reset(all_images)

        all_images = all_images.order_by("path")

        # Se obtienen los formatos de cada uno de los
        special_formats = self.calculate_special_formats_v3(
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
            all_rows = Row.objects.filter(image=image)

            if not all_rows.count():
                set_new_error(
                    self, "La imagen %s no proceso Table Data" % image)
            for row in all_rows:
                seq += 1
                errors = row.get_errors()
                # Intentamos obtener de forma simple el id de la colonia.
                vision_data = row.get_vision_data()

                row_data = []

                for idx, col in enumerate(vision_data):
                    if idx > 2:
                        col_ref = column_types[idx]
                        special_format = special_formats[idx - 3]
                        final_value, c_errors = calculateNumber(
                            col, col_ref, special_format)
                        if len(c_errors):
                            errors += c_errors
                            final_value = None
                    elif idx:
                        final_value = clean_text(col)
                    else:
                        final_value = get_normal_name(col)
                    row_data.append(final_value)

                row.formatted_data = json.dumps(row_data)
                row.sequential = seq
                row.errors = json.dumps(errors)
                row.save()
        # return

    def calculate_special_formats_v3(
            self, all_images, columns_nums, image_num):
        variables = self.get_variables()
        # si ya se había canculado el special_formats, simplemente se obtiene
        # if "special_formats" in variables:
        #     return variables["special_formats"]

        # si no, se calcula:
        # Se trabajará solo con las columnas numéricas, que son las últimas 5
        count_rows = [0, 0, 0, 0, 0]
        special_format_count = [0, 0, 0, 0, 0]
        special_formats = [False, False, False, False, False]
        for image in all_images[:3]:
            for row in image.get_table_data():
                # Se trabajarán solo con los las últimas 5 columnas
                for idx, value in enumerate(row[3:]):
                    sum_col = calculateNumber(value, columns_nums[idx])
                    # Solo se sumarán si la función arrojó algún número
                    if sum_col is not None:
                        special_format_count[idx] += sum_col
                        count_rows[idx] += 1

            # Se puede detarminar una tendencia de tener algún formato
            # especial si existen al menos 5 datos con formato válido
        for idx, col in enumerate(columns_nums):
            curr_tot = float(count_rows[idx])
            is_special = special_format_count[
                idx] / curr_tot >= 0.75 if curr_tot else False
            special_formats.append(is_special)
        variables["special_formats"] = special_formats
        self.variables = json.dumps(variables)
        self.save()
        return special_formats

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


# #Esta función hace una estandarización y limpieza de nombres para facilitar
# #encontrar similitudes entre los nombres oficiales y los que ponen las alcaldías
def cleanSuburbName(text):
    import unidecode
    # Primero estandarizamos los carácteres de español como acentos o eñes
    try:
        final_name = unidecode.unidecode(text).upper()
    except Exception as e:
        print e
        final_name = text.upper()
    # Sustituimos el signo "OR" (|) por I latina
    final_name = re.sub(r'(\|)', 'I', final_name)
    # Nos vamos a quedar con números, letras espacios y muy pocos otros
    # caracteres: guiones bajos y diagonales (slashs) por que con ellos se
    # distinguen algunas colonias. Lo demás, simplemento lo eliminamos:
    final_name = re.sub(ur'[^0-9A-Z\s\(\)\_\-\/\º\.\,]', '', final_name)
    final_name = final_name.upper()
    # Sustituimos puntos, comas y guiones por espacios, lo cuales se añaden sin
    # ningún patrón y sólo contribuyen a reducir el nivel de coincidencia.
    final_name = re.sub(r'[\.\,\-]', ' ', final_name)
    # quitamos dobles espacios
    final_name = re.sub(r' +', ' ', final_name)
    # eliminamos espacios entre paréntesis , ej: ( U HAB ) --> (U HAB)
    final_name = re.sub(r'\(\s?', r'(', final_name)
    final_name = re.sub(r'\s?\)', r')', final_name)
    # Algunos remplazos comunes de alternativas de nombramiento:
    re_uhab = re.compile(
        r'\(\s?(CONJ HAB|UNIDAD HABITACIONAL|U HABS|CONJUNTO HABITACIONAL)\s?\)')
    final_name = re.sub(re_uhab, r'(U HAB)', final_name)
    final_name = re.sub(r'\(\s?(FRACCIONAMIENTO)\s?\)', '(FRACC)', final_name)
    final_name = re.sub(ur'\(\s?(AMPLIACION|AMPLIACIÓN)\s?\)', '(AMPL)', final_name)
    final_name = re.sub(ur'^(COMITE|COMITÉ|COLONIA)\s', '', final_name)
    # Eliminamos la clave en el normal_name (se hace un análisis aparte)
    # La clave de las colonias tiene el formato DD-AAA donde DD es la clave de
    # la alcaldía a dos dígitos AAA es la de la colonia a 3 dígitos.
    # El divisor, el OCR lo puede traducir como cualquier caracter no numérico.
    re_cve = re.compile(r'(\(?\d{2})\s?\D?\s?(\d{3}\)?)')
    final_name = re.sub(re_cve, '', final_name)
    # quitamos espacios al principio y al final
    final_name = final_name.strip()
    # quitamos dobles espacios, de nuevo
    final_name = re.sub(r' +', ' ', final_name)
    return final_name


def get_normal_name(text):
    normal_name = cleanSuburbName(text)
    raw_non_spaces = len(re.sub(r'[^\w]', '', normal_name))
    # Validadores para excluir palabras que ya conocemos y que sabemos que
    # son parte de los encabezados o de los pie de página y no contienen datos.
    if bool(re.search(
            r'(COLONIA O PUEBLO|ORIGINARIO|UNIDAD RESPON)', normal_name)):
        return False
    # Esto significa que llegamos al final, son palabras que no están en ninguna
    # colonia y siempre están en el pie de página.
    elif bool(re.search(r'(REFIERE|REMANENTE|TOTAL|AUTORI|ELABORO|LABORADO|DIRECTOR)',
                        normal_name)):
        return False
    # Ninguna Colonia tiene un nombre tan corto, entonces devolvemos un None
    # para saber que por sí misma no puede ser una colonia, es el caso de que
    # se coma letras de otra columna
    elif raw_non_spaces < 4:
        return None
    return normal_name


def clean_text(text):
    # final_text = unidecode.unidecode(text)
    final_text = text
    final_text = final_text.strip()
    final_text = re.sub(r' +', ' ', final_text)
    final_text = re.sub(r'(\(|\¿|\¡)\s?', '\\1', final_text)
    final_text = re.sub(r'\s?(\)|\:|\,|\.|\;|\?|\!)', '\\1', final_text)
    final_text = re.sub(r'(\)|\:|\,|\.|\;|\?|\!)(\w)', '\\1 \\2', final_text)
    final_text = final_text.strip()
    return final_text
