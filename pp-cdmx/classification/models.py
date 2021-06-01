# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class CategoryIECM(models.Model):
    name = models.CharField(max_length=80, verbose_name=u"Nombre")
    icon = models.CharField(max_length=80, verbose_name=u"Ícono",
                            blank=True, null=True)
    color = models.CharField(max_length=80, verbose_name=u"Color",
                             blank=True, null=True)
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

    is_public = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"Anomalía"
        verbose_name_plural = u"Anomalías"


class CategoryOllin(models.Model):
    name = models.CharField(max_length=255)
    public_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    icon = models.CharField(max_length=30, blank=True, null=True)
    develop_community = models.BooleanField(default=False)
    dictionary_values = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "CategoryOllin"
        verbose_name_plural = "CategoryOllins"

    def __unicode__(self):
        return self.name

    def calculate_value(self, evaluation_text):
        """Valor basado en la precencia independientemente de la cantidad."""
        import re
        import unidecode
        evaluation_text = evaluation_text.lower()
        evaluation_text = unidecode.unidecode(evaluation_text)
        evaluation_text = re.sub(ur'[^a-zA-Z\s]', '', evaluation_text.lower())
        value = 0
        for reference_value, data_list in self.get_dictionary_values().items():
            data_list = list(dict.fromkeys(data_list))
            for data in data_list:
                data = data.lower().strip()
                if not data:
                    continue
                if data in evaluation_text:
                    value += reference_value
        return value

    def get_dictionary_values(self):
        if hasattr(self, "_dictionary_values"):
            return self._dictionary_values
        if not self.dictionary_values:
            return {}
        dictionary_values = {}
        data_line = ""
        value = 0
        for line in self.dictionary_values.split(u"\n"):
            if ":" in line:
                if value:
                    dictionary_values[value] = list(dict.fromkeys([
                        data.strip() for data in data_line.split(",")
                        if data.strip()]))
                try:
                    value = int(line[:line.index(u":")])
                except Exception:
                    continue
                data_line = line[line.index(u":") + 1:]
            else:
                data_line += line
        if value:
            dictionary_values[value] = list(dict.fromkeys([
                data.strip() for data in data_line.split(",")
                if data.strip()]))
        self._dictionary_values = dictionary_values
        return self._dictionary_values
