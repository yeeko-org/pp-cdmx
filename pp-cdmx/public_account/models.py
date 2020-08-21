# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from geographic.models import TownHall
from period.models import PeriodPP


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

    def  column_formatter(self, reset=False):
        #LUCIAN: Esto es solo la continuación de lo que ya comenzaste
        #Lucian, creo que ya no es necesario importar esto:
        from project.models import FinalProject
        import numpy

        suburbs_dict = []
        is_pa_stable = True
        all_orphan_rows= {"suburbs":[], "numbers":[]}
        all_images=PPImage.objects.filter(public_account=self)

        if reset:
            FinalProject.objects\
                .filter(
                    suburb__townhall=self.townhall,
                    period_pp=self.period_pp
                ).update(image=None)


        for image in all_images:
            number_results, len_array = image.calcColumnsNumbers()
            ord_suburbs= image.calculateSuburb()

            standar_dev = numpy.std(len_array)
            is_stable = standar_dev < 1
            if is_stable:
                rows_count = int(round(numpy.mean(len_array)))
                image.rows_count = rows_count
                image.save()

                ord_numbers = []
                amm_types= ["progress", "approved", "modified", "executed", "variation"]
                for idx, row in enumerate(xrange(rows_count)):
                    complete_row = {}
                    is_valid = False
                    for idx_amm,ammount in enumerate(amm_types):
                        try:
                            complete_row[ammount] = number_results[idx_amm][idx]
                        except Exception as e:
                            print e
                    complete_row["seq"] = idx
                    ord_numbers.append(complete_row)
                all_orphan_rows = image.comprobate_stability(all_orphan_rows, 
                                        ord_numbers, ord_suburbs)
            else:
                print "inestable_numbers"
                image.status = "inestable_numbers"
                image.save()
                is_pa_stable = False
                continue



            if is_pa_stable:
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
                    self.save()
                    return
                else:
                    print "hubo algunos datos que no logramos insertar"
                    print new_orphan_rows
                    self.status = "incompleted"
                    self.save()
                    return
            if not is_pa_stable:
                self.status = "inestable_images"
                self.save()

    class Meta:
        verbose_name = u"Cuenta Publica"
        verbose_name_plural = u"Cuentas Publicas"


class PPImage(models.Model):
    public_account = models.ForeignKey(PublicAccount)
    path = models.CharField(max_length=255)
    json_variables = models.TextField(blank=True, null=True)
    clean_data = models.TextField(blank=True, null=True)
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
        return calculateSuburb(
            scraping_suburbs, 
            self.public_account.townhall,
            self)


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
            all_orphan_rows["numbers"]+=ord_numbers
            all_orphan_rows["suburbs"]+=ord_suburbs
            self.status = "inestable_suburbs"
            self.save()
        return all_orphan_rows


    def save_complete_rows(self, ordered_numbers, ordered_suburbs):
        from pprint import pprint
        from project.models import FinalProject
        #LUCIAN: Estoy imprimiendo esto para ayudar a las pruebas
        pprint(ordered_numbers)
        pprint(ordered_suburbs)
        #aquí vas a tomar, en el orden en el que están y los vas a insertar
        is_complete = True
        orphan_rows=[]

        for idx, column_num in enumerate(ordered_numbers):
            sub = ordered_suburbs[idx]
            suburb_id = sub.get("suburb_id")
            if suburb_id:
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

                    pprint(final_proj.__dict__)
                    final_proj.save()
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

        return orphan_rows

        def __unicode__(self):
            return u"%s %s"%(self.public_account, self.path)

        
        
def flexibleMatchSuburb(orphan_subs, pa):
    from geographic.models import Suburb
    from scripts.data_cleaner import similar
    print u"------------------------------------"
    print orphan_subs
    missing_row_idxs = [idx for idx, x in enumerate(orphan_subs) if not x["suburb_id"]]
    missings_subs = Suburb.objects.filter(townhall=pa.townhall,
                finalproject__period_pp=pa.period_pp,
                finalproject__image__isnull=True)
    for sub in missings_subs:
        max_conc = 0
        final_row_idx = -1
        for row_idx in missing_row_idxs:
            concordance = similar(sub.short_name, 
                orphan_subs[row_idx]["raw_normalized"])
            if concordance > 0.8 and concordance > max_conc:
                final_row_idx = row_idx
                max_conc = concordance 
        if final_row_idx > -1:
            orphan_subs[final_row_idx]["suburb_id"] = sub.id
            orphan_subs[final_row_idx]["concordance"] = max_conc
            print "-------------"
            print sub.short_name
            #print orphan_subs[final_row_idx]["raw_normalized"]
            print orphan_subs[final_row_idx]
    return orphan_subs



def formatter_orphan(all_images, all_orphan_rows):
    new_orphan_rows = {"suburbs":[], "numbers":[]}
    print all_orphan_rows
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
