# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from geographic.models import Suburb

from scripts.data_cleaner import set_new_error

amm_types = ["progress", "approved", "modified", "executed", "variation"]


class PPImageOldMix:

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
