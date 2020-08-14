# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from geographic.models import Suburb

from period.models import PeriodPP
from classification.models import CategoryIECM, Anomaly

from django.contrib.auth.models import User
from public_account.models import PPImage


class Project(models.Model):
    suburb = models.ForeignKey(Suburb, verbose_name=u"Colonia")
    period_pp = models.ForeignKey(PeriodPP, verbose_name=u"Periodo PP")
    name_iecm = models.CharField(
        blank=True, null=True,
        max_length=255,
        verbose_name=u"Nombre del IECM")
    project_id = models.IntegerField(
        blank=True, null=True,
        verbose_name=u"ID del Proyecto")
    category_iecm = models.ForeignKey(
        CategoryIECM,
        blank=True,
        null=True,
        verbose_name=u"Categoria IECM")
    votes = models.IntegerField(default=0, verbose_name=u"Votos")
    is_winer = models.BooleanField(
        default=False, verbose_name=u"Es el ganador")

    class Meta:
        verbose_name = "Proyecto de Presupuesto"
        verbose_name_plural = "Proyectos de Presupuestos"

    def __unicode__(self):
        return self.name_iecm


class FinalProject(models.Model):
    suburb = models.ForeignKey(Suburb, verbose_name=u"Colonia")
    period_pp = models.ForeignKey(PeriodPP, verbose_name=u"Periodo PP")
    project = models.ForeignKey(
        Project,
        blank=True,
        null=True,
        verbose_name=u"Proyecto")
    total_votes = models.IntegerField(
        blank=True, null=True, verbose_name=u"Total de Votos")
    description_cp = models.TextField(
        blank=True, null=True, verbose_name=u"Descripcion CP")
    project_cp = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=u"Proyecto CP")
    final_name = models.TextField(
        blank=True,
        null=True,
        verbose_name=u"Nombre Final")
    # category_ollin
    # subcategory

    # Ammounts
    # cambiar a decimal todos los float
    assigned = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True, null=True, verbose_name=u"Asignado")
    approved = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True, null=True, verbose_name=u"Aprobado")
    modified = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True,
        null=True,
        verbose_name=u"Modificado")
    executed = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True, null=True, verbose_name=u"Ejecutado")

    progress = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True, null=True, verbose_name=u"Avance del proyecto")

    # Observations
    manual_capture = models.TextField(
        blank=True, null=True, verbose_name=u"Captura Manual")
    observation = models.TextField(
        blank=True, null=True, verbose_name=u"Observaciones")
    pre_clasification = models.TextField(
        blank=True, null=True, verbose_name=u"Pre-clasificación")
    validated = models.BooleanField(default=False, verbose_name=u"Validado")
    user_validation = models.ForeignKey(
        User, blank=True, null=True, verbose_name=u"Usuario validador")

    image = models.ForeignKey(PPImage, blank=True, null=True)

    # pre_clasification
    # manuela_
    # original_page

    def projects(self):
        return Project.objects\
            .filter(suburb=self.suburb, period_pp=self.period_pp)\
            .distinct()

    class Meta:
        verbose_name = "Proyecto Final en la Cuenta Publica"
        verbose_name_plural = "Proyectos Finales en la Cuenta Publica"

    def __unicode__(self):
        return u"%s - %s" % (self.suburb, self.period_pp)


class AnomalyFinalProject(models.Model):
    anomaly = models.ForeignKey(Anomaly)
    final_project = models.ForeignKey(FinalProject)

    def __unicode__(self):
        return u"%s -%s" % (self.final_project, self.anomaly)

    class Meta:
        verbose_name_plural = u"Anomalía y Proyecto Final"
        verbose_name = u"Anomalía y Proyecto Final"
