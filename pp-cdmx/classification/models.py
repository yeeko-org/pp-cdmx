# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class CategoryIECM(models.Model):
    name = models.CharField(max_length=80, verbose_name=u"Nombre")
    year_start = models.IntegerField(
        verbose_name=u"Año de Inicio", blank=True, null=True)
    year_end = models.IntegerField(
        verbose_name=u"Año de Fin", blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Categoria IECM"
        verbose_name_plural = "Categorias IECM"


class Anomaly(models.Model):
    name = models.CharField(max_length=250, verbose_name=u"Nombre")
    description = models.TextField(
        blank=True, null=True, verbose_name=u"Descripción")
    rules = models.TextField(blank=True, null=True, verbose_name=u"Reglas")
    color = models.CharField(
        max_length=30, blank=True, null=True,
        verbose_name=u"Color")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"Anomalía"
        verbose_name_plural = u"Anomalías"
