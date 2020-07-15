# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from ckeditor.fields import RichTextField


class LawPP(models.Model):
    publish_year = models.IntegerField(verbose_name=u"Año de publicacion")
    name = models.TextField(verbose_name=u"Nombre")
    file_law = models.FileField(
        upload_to="law_pp",
        blank=True,
        null=True,
        verbose_name=u"Archivo de Ley")
    summary = RichTextField(blank=True, null=True, verbose_name=u"Contenido")

    class Meta:
        verbose_name = u"Ley Reglamentaria del Presupuesto Participativo"
        verbose_name_plural = u"Leyes Reglamentarias del Presupuesto Participativo"

    def __unicode__(self):
        return self.name


class PeriodPP(models.Model):
    year = models.IntegerField(verbose_name=u"Año")
    is_public = models.BooleanField(default=False, verbose_name=u"Es Publico")
    law_pp = models.ForeignKey(
        LawPP,
        blank=True,
        null=True,
        verbose_name=u"Ley Reglamentaria del PP")
    pdf_iedf = models.FileField(
        blank=True,
        null=True,
        upload_to="period_pp",
        verbose_name=u"Archivo PDF del IEDF")

    class Meta:
        verbose_name = u"Periodo de Presupuesto Participativo"
        verbose_name_plural = u"Periodos de Presupuesto Participativo"

    def __unicode__(self):
        return unicode(self.year)
