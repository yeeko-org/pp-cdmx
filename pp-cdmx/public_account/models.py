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

    def  column_formatter(self):
        import numpy
        suburbs_dict = []
        th = self.townhall
        period = self.period_pp
        for image in PPImage.objects.filter(public_account=self):
            number_results, len_array = image.calcColumnsNumbers()
            standar_dev = numpy.std(len_array)
            is_stable = standar_dev < 1
            if image.json_variables:
                init_json = json.loads(image.json_variables)
            else:
                init_json = {}
            init_json["is_stable"] = is_stable
            if is_stable:
                number_of_rows = round(numpy.mean(len_array))

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

    def __unicode__(self):
        return u"%s %s"%(self.public_account, self.path)
