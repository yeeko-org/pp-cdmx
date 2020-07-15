# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class CategoryIEDF(models.Model):
    name = models.CharField(max_length=80, verbose_name=u"Nombre")
    year_start = models.IntegerField(
        verbose_name=u"Año de Inicio", blank=True, null=True)
    year_end = models.IntegerField(
        verbose_name=u"Año de Fin", blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Categoria IEDF"
        verbose_name_plural = "Categorias IEDF"
