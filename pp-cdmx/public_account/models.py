# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from geographic.models import TownHall
from period.models import PeriodPP
from pprint import pprint


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
        verbose_name=u"Alcaldia")
    # pages = models.TextField(blank=True, null=True, verbose_name=u"Paginas")
    period_pp = models.ForeignKey(PeriodPP, verbose_name=u"Periodo PP")
    variables = models.TextField(blank=True, null=True)
    status = models.CharField(
        blank=True, null=True, max_length=80, default=u"uncleaned")

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
            all_images = all_images[image_num-1:image_num]

        if reset:
            FinalProject.objects\
                .filter(suburb__townhall=self.townhall,
                    period_pp=self.period_pp)\
                .update(image=None)
            PPImage.objects.filter(public_account=self).update(error_cell=None)

        for image in all_images:
            print image.path
            number_results, len_array = image.calcColumnsNumbers()
            ord_suburbs= image.calculateSuburb()

            standar_dev = numpy.std(len_array)
            is_stable = standar_dev <= 0.8
            print len_array
            ord_numbers = []
            if is_stable:
                print "la imagen es estable"
                rows_count = int(round(numpy.mean(len_array)))
                image.rows_count = rows_count
                image.save()

                amm_types= ["progress", "approved", "modified", "executed", "variation"]
                for idx, row in enumerate(xrange(rows_count)):
                    complete_row = {}
                    is_valid = False
                    for idx_amm,ammount in enumerate(amm_types):
                        try:
                            complete_row[ammount] = number_results[idx_amm][idx]
                        except Exception as e:
                            print ammount
                            print row
                            print e
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
            return
        if is_pa_stable or True:
            #si existen filas huérfanos:
            len_orphan = len(all_orphan_rows)
            new_orphan_rows = []
            if len_orphan:
                print "haremos un match suavizado"
                orphan_subs = all_orphan_rows["suburbs"]
                all_orphan_rows["suburbs"] = flexibleMatchSuburb(orphan_subs, self)
                new_orphan_rows = formatter_orphan(all_images, all_orphan_rows)
                len_new_orphan = len(new_orphan_rows)
            if not len_orphan or not len_new_orphan:
                self.status = "completed"
            else:
                print "hubo algunos datos que no logramos insertar"
                #print new_orphan_rows
                self.status = "incompleted"
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
    data_row_numbers=models.TextField(blank=True, null=True)
    status = models.CharField(
        blank=True, null=True, max_length=80, default=u"uncleaned")
    rows_count = models.IntegerField(blank=True, null=True)
    def get_json_variables(self):
        import json
        try:
            return json.loads(self.json_variables)
        except Exception as e:
            print e
            return {}
    def calcColumnsNumbers(self):
        import json
        from scripts.data_cleaner import calcColumnsNumbers
        scraping_numbers=self.get_json_variables().get("2", {})
        column_values, len_array = calcColumnsNumbers(scraping_numbers)
        try:
            self.data_row_numbers = json.dumps(column_values)
            self.save()
        except Exception as e:
            print e
        return column_values, len_array

    def calculateSuburb(self):
        scraping_suburbs=self.get_json_variables().get("1", {})
        from scripts.data_cleaner import calculateSuburb
        return calculateSuburb(scraping_suburbs, self)

    def set_new_error(self, text_error):
        current_notes = self.error_cell
        print text_error
        self.error_cell = "%s\n%s"%(current_notes, text_error)
        self.save()


    def comprobate_stability(self, all_orphan_rows, ord_numbers, ord_suburbs):
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
            print "inestable_suburbs"
            print len(ord_numbers)
            print len(ord_suburbs)
            print len(real_ord_suburbs)
            print self.path
            all_orphan_rows["numbers"]+=ord_numbers
            all_orphan_rows["suburbs"]+=ord_suburbs
            self.status = "inestable_suburbs"
            self.save()
        return all_orphan_rows


    def save_complete_rows(self, ordered_numbers, ordered_suburbs):
        from pprint import pprint
        from project.models import FinalProject
        #LUCIAN: Estoy imprimiendo esto para ayudar a las pruebas
        #pprint(ordered_numbers)
        #pprint(ordered_suburbs)
        #aquí vas a tomar, en el orden en el que están y los vas a insertar
        is_complete = True
        orphan_rows=[]

        for idx, column_num in enumerate(ordered_numbers):
            sub = ordered_suburbs[idx]
            suburb_id = sub.get("suburb_id")
            if suburb_id:
                if type(suburb_id) == int:
                    final_proj = FinalProject.objects.filter(
                        suburb__id=suburb_id,
                        period_pp=self.public_account.period_pp).first()
                    if final_proj:
                        final_proj.approved = column_num.get("approved", {}).get("final_value")
                        final_proj.modified = column_num.get("modified", {}).get("final_value")
                        final_proj.executed = column_num.get("executed", {}).get("final_value")
                        final_proj.progress = column_num.get("progress", {}).get("final_value")
                        final_proj.variation = column_num.get("variation", {}).get("final_value")
                        final_proj.image=self

                        #pprint(final_proj.__dict__)
                        final_proj.save()
                else:
                    print "no es de tipo int"
                    print suburb_id
                    print column_num
                    final_proj = False

            else:
                final_proj=False

            if not final_proj:
                sub["number_data"] = column_num
                orphan_rows.append(sub)
                is_complete=False
                # continue

        if is_complete:
            self.status = "completed"
            print "completed"
        else:
            self.status = "stable_row"
            print "Hay cosas que faltan por completar"

        self.save()

        #pprint(orphan_rows)
        return orphan_rows

        def __unicode__(self):
            return u"%s %s"%(self.public_account, self.path)

def similar_content(sub_name, row):
    try:
        sim_alone = SequenceMatcher(None, sub_name, row["curr"]).ratio()
    except Exception as e:
        sim_alone = 0
    sim_comb = 0
    if not row["can_be_comb"]:
        try:
            sim_comb = SequenceMatcher(None, sub_name, row["comb"]).ratio()
        except Exception as e:
            pass
    sim = max([sim_alone, sim_comb])
    mayor = 'comb' if sim_comb > sim_alone else 'curr' if sim_alone else None
    return [mayor, sim]
        
def flexibleMatchSuburb(orphan_subs, pa):
    from geographic.models import Suburb
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
            try:
                invalid = orphan_subs[row_idx]["invalid"]
                continue
            except Exception as e:
                pass
            may, concordance = similar_content(sub.short_name, orphan_subs[row_idx])
            if concordance > 0.8 and concordance > max_conc:
                final_row_idx = row_idx
                next_bigger = may == 'comb'
                max_conc = concordance 
        if final_row_idx > -1:
            #print final_row_idx
            sel_row = orphan_subs[final_row_idx]
            image_id = sel_row["image_id"]
            image = PPImage.objects.get(id=image_id)
            sub_id = saveFinalProjSuburb(sub.id, image)
            print "-------------"
            print sub_id
            if sub_id:
                orphan_subs[final_row_idx]["suburb_id"] = sub.id
                orphan_subs[final_row_idx]["concordance"] = max_conc
                if next_bigger:
                    print "FUE DE TIPO NEXT_BIGGER"
                    orphan_subs[final_row_idx]["type_comb"] = 'comb'
                    try:
                        id_next = [idx for idx, x in enumerate(orphan_subs)
                            if x["image_id"]==sel_row["image_id"] and
                            x["seq"] == sel_row["seq"]+1]
                        if len(id_next):
                            print "HAY UN REGISTRO!!!!"
                            print id_next[0]
                            print orphan_subs[id_next[0]]
                            orphan_subs[id_next[0]]["invalid"] = True
                        else:
                            print "No existieron coincidencias..."
                    except Exception as e:
                        print "hubo un error:"
                        print e
                else:
                    orphan_subs[final_row_idx]["type_comb"] = 'curr'
            else:
                print "!!! YA TENÍAMOS Y NO SE PUDO"
        else:
            print sub.short_name

    missing_row = [x for x in orphan_subs if not x["suburb_id"]]
    if (len(missing_row)):
        print "las no matcheadas:"
        pprint(missing_row)
        print u"------------------------------------"
    missings_subs_last = Suburb.objects.filter(townhall=pa.townhall,
                finalproject__period_pp=pa.period_pp,
                finalproject__image__isnull=True)
    print missings_subs_last
    """for m_sub in missings_subs_last:
        nueva = question_console(m_sub, missing_row)
        if nueva == False:
            break"""
    return orphan_subs


def question_console(sub, rows):
    all_lines = ""
    print sub.short_name
    print u"\n Posibles coincidencias: \n\n"
    print "0 --> Ninguna coincide"
    for idx, row in enumerate(rows):
        print "%s --> %s"%(idx+1, row["curr"])
        if row["can_be_comb"]:
            try:
                print "(compl) --> %s"(idx+1, row["comb"])
            except:
                pass
    print "Escribe una letra (con comillas) para interrumpir el proceso"
    answer = input("Escribe el numero que coincida con : ")
    print answer
    if type(answer) == int:
        resp = rows[answer]
        #question_save(sub, resp)
    #else:
        #return False

def question_save(sub, resp):
    print "0 --> Que no se guarde como variable"
    print "1 --> %s"%resp["curr"]
    if resp["can_be_comb"]:
        try:
            print "2 --> %s"%resp["comp"] 
        except:
            print "no econtramos el complemento"
    answer = input("Quieres que se guarde como variable (0 / 1 / 2) ?")
    print answer
    if type(answer) == int:
        if answer == 1:
            sub.compact_name = resp["curr"]
            sub.save()
        if answer == 2:
            sub.compact_name = resp["comb"]
            sub.save()
        return

        

    """if answer == 1: 
        print "Hará algo con 1"
    elif answer == 2: 
        print "Hará algo con 2"
    else: 
        print("Please enter yes or no.") """



def formatter_orphan(all_images, all_orphan_rows):
    new_orphan_rows = {"suburbs":[], "numbers":[]}
    #print all_orphan_rows
    for image in all_images:
        current_suburbs = [x for x in all_orphan_rows["suburbs"] if x["image_id"] == image.id]
        current_numbers = [x for x in all_orphan_rows["numbers"] if x["image_id"] == image.id]
        #signfica que no coincidieron las columnas de ambos recortes:
        if len(current_numbers):
            new_orphan_rows = image.comprobate_stability(new_orphan_rows, 
                                    current_numbers, current_suburbs)
        else:
            orphan_stable_subs = image.save_complete_rows(current_numbers,
                                                             current_suburbs)
            new_orphan_rows["suburbs"]+=orphan_stable_subs
    return new_orphan_rows
