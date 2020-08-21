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

    def __unicode__(self):
        return u"%s -- %s"%(self.period_pp, self.townhall)

    class Meta:
        verbose_name = u"Cuenta Publica"
        verbose_name_plural = u"Cuentas Publicas"


class PPImage(models.Model):
    public_account = models.ForeignKey(PublicAccount)
    path = models.CharField(max_length=255)
    json_variables = models.TextField(blank=True, null=True)
    clean_data = models.TextField(blank=True, null=True)
    number_of_rows=models.TextField(blank=True, null=True)
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
            self.number_of_rows = json.dumps(column_values)
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
