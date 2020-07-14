# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from ckeditor.fields import RichTextField


class LawPP(models.Model):
    publish_year = models.IntegerField()
    name = models.TextField()
    file_law = models.FileField(upload_to="law_pp", blank=True, null=True)
    summary = RichTextField(blank=True, null=True)

    class Meta:
        verbose_name = u"Ley Reglamentaria del Presupuesto Participativo"
        verbose_name_plural = u"Leyes Reglamentarias del Presupuesto Participativo"

    def __unicode__(self):
        return self.name


class PeriodPP(models.Model):
    year = models.IntegerField()
    is_public = models.BooleanField(default=False)
    law_pp = models.ForeignKey(LawPP, blank=True, null=True)
    excel_iedf = models.FileField(upload_to="period_pp")

    class Meta:
        verbose_name = u"Periodo de Presupuesto Participativo"
        verbose_name_plural = u"Periodos de Presupuesto Participativo"

    def __unicode__(self):
        return self.year
