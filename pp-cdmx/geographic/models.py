# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class TownHall(models.Model):
    cve_inegi = models.CharField(max_length=6, verbose_name="Clave INEGI")
    cve_alc = models.IntegerField(verbose_name=u"Clave de la Alcaldia")
    name = models.CharField(max_length=30, verbose_name=u"Nombre")
    short_name = models.CharField(max_length=12, verbose_name=u"Nombre Corto")
    image = models.ImageField(upload_to="townhall", verbose_name=u"Imagen")

    def __unicode__(self):
        return self.short_name or self.name

    class Meta:
        verbose_name = u"Alcaldia"
        verbose_name_plural = u"Alcaldias"


class TownHallGeoData(models.Model):
    townhall = models.OneToOneField(TownHall)
    geo_point = models.TextField()
    geo_shape = models.TextField()

    def __unicode__(self):
        return self.townhall


class SuburbType(models.Model):
    name = models.CharField(max_length=120)
    abrev = models.CharField(blank=True, null=True, max_length=40)
    icon = models.CharField(blank=True, null=True, max_length=30)
    emoji = models.CharField(blank=True, null=True, max_length=6)

    class Meta:
        verbose_name = u"Tipo de Colonia/Asentamiento"
        verbose_name_plural = u"Tipos de Colonia/Asentamiento"

    def __unicode__(self):
        return self.name


class Suburb(models.Model):
    cve_col = models.CharField(max_length=8)
    name = models.CharField(max_length=140)
    short_name = models.CharField(blank=True, null=True, max_length=140)
    townhall = models.ForeignKey(TownHall, verbose_name=u"Alcaldia")
    sururb_type = models.ForeignKey(SuburbType)
    is_pilot = models.BooleanField(default=False)
    start_year = models.IntegerField(default=2010)
    end_year = models.IntegerField(blank=True, null=True)
    derivation_suburb = models.ForeignKey(
        "Suburb", blank=True, null=True, related_name="childrens_suburb")
    pob_2010 = models.IntegerField(blank=True, null=True)
    pob_2015 = models.IntegerField(blank=True, null=True)
    pob_2020 = models.IntegerField(blank=True, null=True)
    secc_com = models.TextField(
        blank=True, null=True, verbose_name=u"Seccion Completa")
    secc_parc = models.TextField(
        blank=True, null=True, verbose_name=u"Seccion Parcial")

    class Meta:
        verbose_name = "Colonia"
        verbose_name_plural = "Colonias"

    def __unicode__(self):
        return self.name or self.short_name


class SuburbGeoData(models.Model):
    suburb = models.OneToOneField(Suburb)
    geo_point = models.CharField(max_length=40)
    geo_shape = models.TextField()
    geo_topo = models.TextField()

    def __unicode__(self):
        return self.suburb
