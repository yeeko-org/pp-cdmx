# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class TownHall(models.Model):
    cve_inegi = models.CharField(
        max_length=6,
        verbose_name="Clave INEGI")
    cve_alc = models.IntegerField(
        verbose_name=u"Clave de la Alcaldia")
    name = models.CharField(
        max_length=30,
        verbose_name=u"Nombre")
    short_name = models.CharField(
        max_length=12, blank=True, null=True,
        verbose_name=u"Nombre Corto")
    image = models.ImageField(
        blank=True, null=True,
        upload_to="townhall",
        verbose_name=u"Imagen")

    def __unicode__(self):
        return self.short_name or self.name

    class Meta:
        verbose_name = u"Alcaldía"
        verbose_name_plural = u"Alcaldías"


class TownHallGeoData(models.Model):
    townhall = models.OneToOneField(TownHall, verbose_name=u"Alcaldia")
    geo_point = models.TextField(verbose_name=u"geo point")
    geo_shape = models.TextField(verbose_name=u"geo shape")

    def __unicode__(self):
        return unicode(self.townhall)


class SuburbType(models.Model):
    name = models.CharField(
        max_length=120,
        verbose_name=u"Nombre")
    abrev = models.CharField(
        max_length=40, blank=True, null=True,
        verbose_name=u"Abreviatura")
    icon = models.CharField(
        max_length=30, blank=True, null=True,
        verbose_name=u"Icon")
    emoji = models.CharField(
        max_length=6, blank=True, null=True,
        verbose_name=u"Emoji")

    class Meta:
        verbose_name = u"Tipo de Colonia/Asentamiento"
        verbose_name_plural = u"Tipos de Colonia/Asentamiento"

    def __unicode__(self):
        return self.name


class Suburb(models.Model):
    cve_col = models.CharField(
        max_length=8,
        verbose_name=u"Clave de la Colonia")
    name = models.CharField(
        max_length=140,
        verbose_name=u"Nombre")
    short_name = models.CharField(
        max_length=140, blank=True, null=True,
        verbose_name=u"Nombre  Corto")
    townhall = models.ForeignKey(
        TownHall, verbose_name=u"Alcaldia")
    suburb_type = models.ForeignKey(
        SuburbType, blank=True, null=True,
        verbose_name=u"Tipo de colonia")
    is_pilot = models.BooleanField(
        default=False, verbose_name=u"¿Es Piloto?")
    start_year = models.IntegerField(
        default=2010, verbose_name=u"Año de inicio")
    end_year = models.IntegerField(
        blank=True, null=True,
        verbose_name=u"Año de Fin")
    derivation_suburb = models.ForeignKey(
        "Suburb", blank=True, null=True,
        related_name="childrens_suburb",
        verbose_name=u"Colonia derivada de ")
    pob_2010 = models.IntegerField(
        blank=True, null=True,
        verbose_name=u"Poblacion en 2010")
    pob_2015 = models.IntegerField(
        blank=True, null=True,
        verbose_name=u"Poblacion en 2015")
    pob_2020 = models.IntegerField(
        blank=True, null=True,
        verbose_name=u"Poblacion en 2020")
    secc_com = models.TextField(
        blank=True, null=True,
        verbose_name=u"Seccion Completa")
    secc_parc = models.TextField(
        blank=True, null=True,
        verbose_name=u"Seccion Parcial")

    def final_projects(self):
        from project.models import FinalProject
        return FinalProject.objects.filter(suburb=self)

    class Meta:
        verbose_name = "Colonia"
        verbose_name_plural = "Colonias"

    def __unicode__(self):
        return self.name or self.short_name


class SuburbGeoData(models.Model):
    suburb = models.OneToOneField(Suburb, verbose_name=u"Colonia")
    geo_point = models.CharField(max_length=40, verbose_name=u"geo point")
    geo_shape = models.TextField(verbose_name=u"geo shape")
    geo_topo = models.TextField(verbose_name=u"geo topo")

    def __unicode__(self):
        return unicode(self.suburb)
