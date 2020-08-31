# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from geographic.models import TownHall, Suburb
from period.models import PeriodPP
from pprint import pprint
from scripts.data_cleaner import set_new_error

amm_types= ["progress", "approved", "modified", "executed", "variation"]

class PublicAccount(models.Model):
    # original_pdf = models.FileField(
    #     upload_to="public_account",
    #     blank=True,
    #     null=True,
    #     verbose_name=u"PDF original")
    townhall = models.ForeignKey(
        TownHall,
        blank=True,
        null=True,
        verbose_name=u"Alcaldía")
    # pages = models.TextField(blank=True, null=True, verbose_name=u"Paginas")
    period_pp = models.ForeignKey(PeriodPP, verbose_name=u"Periodo PP")
    variables = models.TextField(blank=True, null=True)
    status = models.CharField(
        blank=True, null=True, max_length=80, default=u"uncleaned")
    error_cell = models.TextField(blank=True, null=True, 
        verbose_name="pila de errores")    

    def __unicode__(self):
        return u"%s -- %s"%(self.period_pp, self.townhall)

    def column_formatter(self, reset=False, image_num=None):
        #LUCIAN: Esto es solo la continuación de lo que ya comenzaste
        #Lucian, creo que ya no es necesario importar esto:
        from project.models import FinalProject
        import numpy
        from pprint import pprint

        suburbs_dict = []
        is_pa_stable = True
        all_orphan_rows= {"suburbs":[], "numbers":[]}
        all_images=PPImage.objects.filter(public_account=self)
        if image_num:
            all_images = all_images.filter(path__icontains=image_num)

        if reset:
            FinalProject.objects\
                .filter(suburb__townhall=self.townhall,
                        period_pp=self.period_pp,
                        image__in=all_images)\
                .update(image=None, similar_suburb_name=None)
            PPImage.objects.filter(public_account=self).update(error_cell=None)
            self.error_cell = ""
            self.save()
        for image in all_images:
            print image.path
            ord_suburbs= image.calcColumns('suburbs')

            number_results, len_array = image.calcColumns('numbers')
            standar_dev = numpy.std(len_array)
            if standar_dev > 0:
                print u"vamos a ir por un cálculo estricto"
                number_results_stict, len_array_sctict = image.calcColumns(
                    'numbers', True)
                standar_dev_stict = numpy.std(len_array_sctict)
                if standar_dev_stict < standar_dev:
                    print u"el no estricto es %s"%len_array
                    number_results = number_results_stict
                    len_array = len_array_sctict
                    standar_dev = numpy.std(len_array)
                    image.len_array_numbers = len_array
                    image.data_row_numbers = number_results_stict
                    image.save()
                else:
                    print "no mejora el len_array"
                    print u"el estricto es %s"%len_array_sctict
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
                            complete_row[ammount] = number_results[idx_amm][idx]
                        except Exception as e:
                            #print ammount
                            #print row
                            #print e
                            pass
                    complete_row["seq"] = idx
                    complete_row["image_id"] = image.id
                    ord_numbers.append(complete_row)
                all_orphan_rows = image.comprobate_stability(all_orphan_rows, 
                                        ord_numbers, ord_suburbs)
            else:
                print "inestable_numbers"
                image.status = "inestable_numbers"
                image.save()
                is_pa_stable = False
                set_new_error(image, u"No todas las columnas numéricas coinciden")
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
            #return
        if is_pa_stable or True:
            #si existen filas huérfanos:
            len_orphan = len(all_orphan_rows)
            new_orphan_rows = []
            subs_alone = None
            new_orphan_subs = None
            if len_orphan:
                print "haremos un match suavizado"
                orphan_subs = all_orphan_rows["suburbs"]
                new_orphan_subs = flexibleMatchSuburb(orphan_subs, self)
                all_orphan_rows["suburbs"] = new_orphan_subs
                new_orphan_rows = formatter_orphan(all_images, all_orphan_rows)
                len_new_orphan = len(new_orphan_rows)


            missings_subs = Suburb.objects.filter(
                townhall=self.townhall,
                finalproject__period_pp=self.period_pp,
                finalproject__image__isnull=True)

            incomp_images = PPImage.objects.filter(public_account=self)\
                                            .exclude(status='completed')


            self.status = "incompleted" if incomp_images.count() else 'completed'

            if missings_subs.count():
                set_new_error(self, 'Faltan las siguientes Colonias:')
            for sub in missings_subs:
                set_new_error(self, "%s %s"%(sub.cve_col, sub.name))

        if not is_pa_stable:
            self.status = "inestable_images"
        self.save()
        return

    class Meta:
        verbose_name = u"Cuenta Publica"
        verbose_name_plural = u"Cuentas Publicas"


class PPImage(models.Model):
    public_account = models.ForeignKey(PublicAccount)
    path = models.CharField(max_length=255)
    json_variables = models.TextField(blank=True, null=True)
    clean_data = models.TextField(blank=True, null=True)
    error_cell = models.TextField(blank=True, null=True, 
        verbose_name="pila de errores")
    len_array_numbers = models.CharField(max_length=80, 
        blank=True, null=True)
    data_row_numbers=models.TextField(blank=True, null=True, 
        verbose_name=u"Datos de columnas numéricas")
    data_row_suburbs=models.TextField(blank=True, null=True,
        verbose_name=u"Datos de columna de suburbs")
    status = models.CharField(
        blank=True, null=True, max_length=80, default=u"uncleaned")
    def get_json_variables(self):
        import json
        try:
            return json.loads(self.json_variables)
        except Exception as e:
            print e
            return {}

    def calcColumns(self, type_col, strict=False):
        import json
        from scripts.data_cleaner import calcColumnsNumbers, calculateSuburb
        is_sub = type_col == 'suburbs'
        cut = '1' if is_sub else '2'
        scraping_values=self.get_json_variables().get(cut, {})
        if is_sub:
            column_values = calculateSuburb(scraping_values, self)
        else:
            column_values, len_array = calcColumnsNumbers(scraping_values, strict)
        if not strict:
            try:
                #self['data_row_%s'%type_col] = json.dumps(column_values)
                setattr(self, 'data_row_%s'%type_col, json.dumps(column_values))
                if not is_sub:
                    self.len_array_numbers = json.dumps(len_array)
                self.save()
            except Exception as e:
                set_new_error(self, "No logramos guardar columnas %s -->"%type_col)
                set_new_error(self, e)
        return column_values if is_sub else (column_values, len_array)

    def comprobate_stability(self, all_orphan_rows, ord_numbers, 
                            ord_suburbs, final_compr=False, from_last=False):
        stable_row = len(ord_numbers) == len(ord_suburbs)
        if not stable_row:
            real_ord_suburbs = [x for x in ord_suburbs if x["suburb_id"]]
            if len(ord_numbers) == len(real_ord_suburbs):
                stable_row = True
                ord_suburbs = real_ord_suburbs
        #el número de columnas coincide:
        if stable_row:
            orphan_stable_subs = self.save_complete_rows(
                ord_numbers, ord_suburbs)
            all_orphan_rows["suburbs"]+=orphan_stable_subs
        else:
            all_orphan_rows["numbers"]+=ord_numbers
            all_orphan_rows["suburbs"]+=ord_suburbs
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
            print u"%s --> %s"%(sub.id, sub.short_name)

        missing_rows_idxs = [idx for idx, x in enumerate(ord_suburbs) if not x["suburb_id"]]
        print u"---------------------------------"
        print u"ESTAS SON LAS COLUMNAS POSIBLES:"
        for miss_idx in missing_rows_idxs:
            print "%s --> %s"%(miss_idx+1, ord_suburbs[miss_idx]['curr'])
            try:
                print "   COMB| %s"%(ord_suburbs[miss_idx]['comb'])
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
                        ord_suburbs[answer_2-1]["suburb_id"] = sub_id
                        has_new_data = True
                    else:
                        print u"!!NO ECONTRAMOS LO QUE DESEABAS!!"
                    continue
        if has_new_data:
            for_not_error = {"suburbs":[], "numbers":[]}
            self.comprobate_stability(for_not_error, ord_numbers, 
                ord_suburbs, False, True)

    def save_complete_rows(self, ordered_numbers, ordered_suburbs):
        from pprint import pprint
        from project.models import FinalProject
        #LUCIAN: Estoy imprimiendo esto para ayudar a las pruebas
        #pprint(ordered_numbers)
        #pprint(ordered_suburbs)
        #aquí vas a tomar, en el orden en el que están y los vas a insertar
        is_complete = True
        orphan_rows=[]
        has_numbers = len(ordered_numbers)
        base_for_enum = ordered_numbers if has_numbers else ordered_suburbs

        for idx, column_num in enumerate(base_for_enum):
            sub_row = ordered_suburbs[idx]
            if has_numbers:
                ordered_suburbs[idx]["number_data"] = column_num
            suburb_id = sub_row.get("suburb_id")
            if suburb_id:
                if type(suburb_id) == int:
                    final_proj = FinalProject.objects.filter(
                        suburb__id=suburb_id,
                        period_pp=self.public_account.period_pp).first()
                    if final_proj:
                        self.set_values_final_proj(final_proj, sub_row)
                else:
                    print "!!!!!no es de tipo int (save_complete_rows)"
                    set_new_error(self,
                        u"guardamos el sub_id como '%s' (no numérico)"%suburb_id)
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

        #pprint(orphan_rows)
        return orphan_rows

    def __unicode__(self):
        return u"%s %s"%(self.public_account, self.path)


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
                    set_new_error(final_proj, u"%s >> formato incorrecto: %s"%(
                                    ammount, curr_amm.get("raw_unity")))
            else:
                set_new_error(final_proj,
                        u"%s >> No tiene ningún valor "%ammount)

            final_proj.image=self 
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
    new_orphan_rows = {"suburbs":[], "numbers":[]}
    #print all_orphan_rows
    for image in all_images:
        current_suburbs = [x for x in all_orphan_rows["suburbs"] if x["image_id"] == image.id]
        current_numbers = [x for x in all_orphan_rows["numbers"] if x["image_id"] == image.id]
        print "--------------------------"
        #print current_numbers
        #print current_suburbs
        #signfica que no coincidieron las columnas de ambos recortes:
        if len(current_numbers):
            print u"sí hay numbers"
            print image.path
            new_orphan_rows = image.comprobate_stability(new_orphan_rows, 
                                    current_numbers, current_suburbs, True)
        else:
            print u"no hay numbers"
            print image.path
            orphan_stable_subs = image.save_complete_rows(current_numbers,
                                                             current_suburbs)
            new_orphan_rows["suburbs"]+=orphan_stable_subs
    return new_orphan_rows


def flexibleMatchSuburb(orphan_subs, pa):
    from scripts.data_cleaner import similar, saveFinalProjSuburb
    from pprint import pprint
    print u"------------------------------------"
    #print orphan_subs
    missing_row_idxs = [idx for idx, x in enumerate(orphan_subs) if not x["suburb_id"]]
    missings_subs = Suburb.objects.filter(townhall=pa.townhall,
                finalproject__period_pp=pa.period_pp,
                finalproject__image__isnull=True)
    for sub in missings_subs:
        max_conc = 0
        final_row_idx = -1
        for row_idx in missing_row_idxs:
            if orphan_subs[row_idx]["invalid"]:
                continue
            may, concordance = similar_content(sub.short_name, orphan_subs[row_idx])
            #print "%s -- %s"%(may, concordance)
            if concordance > 0.8 and concordance > max_conc:
                final_row_idx = row_idx
                may_type = may
                #comb_bigger = may == 'comb'
                #triple_bigger = may == 'triple'
                max_conc = concordance 
        if final_row_idx > -1:
            #print final_row_idx
            sel_row = orphan_subs[final_row_idx]
            image_id = sel_row["image_id"]
            image = PPImage.objects.get(id=image_id)
            sub_id = saveFinalProjSuburb(sub.id, image, max_conc)
            #print "-------------"
            #print sub_id
            if sub_id:
                orphan_subs[final_row_idx]["suburb_id"] = sub.id
                orphan_subs[final_row_idx]["concordance"] = max_conc
                orphan_subs[final_row_idx]["type_comb"] = may_type
                if may_type != 'curr':
                    orphan_subs = set_values_combs(orphan_subs, sel_row, 
                        image, may_type)
            else:
                set_new_error(image,
                    "No se encontró el sub %s que ya habíamos seteado"%sub.id)
        #else:
            #print sub.short_name
    return orphan_subs


def set_values_combs(orphan_subs, sel_row, image, may_type):
    is_triple = may_type == 'triple'
    all_next = [1, 2] if is_triple else [1]
    for next_req in all_next:
        try:
            id_next = [idx for idx, x in enumerate(orphan_subs)
                        if x.get("image_id") == image.id and
                            x.get("seq") == sel_row.get("seq")+next_req]
            if len(id_next):
                orphan_subs[id_next[0]]["invalid"] = True
            else:
                #print "No existieron coincidencias..."
                pass
        except Exception as e:
            set_new_error(image,
                "No se encontró el seq %s para ponerlo como ínválido")
            print e
    return orphan_subs

