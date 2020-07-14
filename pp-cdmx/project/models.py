# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from geographic.models import Suburb

from period.models import PeriodPP
from classification.models import CategoryIEDF

from django.contrib.auth.models import User


class Project(models.Model):
    suburb = models.ForeignKey(Suburb)
    period_pp = models.ForeignKey(PeriodPP)
    name_iedf = models.CharField(max_length=255)
    project_id = models.IntegerField()
    category_iedf = models.ForeignKey(CategoryIEDF, blank=True, null=True)
    votes = models.IntegerField(default=0)
    is_winer = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Proyecto de Presupuesto"
        verbose_name_plural = "Proyectos de Presupuestos"

    def __unicode__(self):
        return self.name_iedf


class FinalProject(models.Model):
    suburb = models.ForeignKey(Suburb)
    period_pp = models.ForeignKey(PeriodPP)
    project = models.ForeignKey(Project, blank=True, null=True)
    total_votes = models.IntegerField(blank=True, null=True)
    description_cp = models.TextField(blank=True, null=True)
    final_name = models.TextField(blank=True, null=True)
    category_cp = models.CharField(max_length=255, blank=True, null=True)
    # category_ollin
    # subcategory
    total_votes = models.TextField(blank=True, null=True)

    # Ammounts
    assigned = models.FloatField(blank=True, null=True)
    approuved = models.FloatField(blank=True, null=True)
    modified = models.FloatField(blank=True, null=True)
    excecuted = models.FloatField(blank=True, null=True)
    progress = models.IntegerField(blank=True, null=True)

    # Observations
    observation = models.TextField(blank=True, null=True)
    validated = models.BooleanField(default=False)
    user_validation = models.ForeignKey(User, blank=True, null=True)
    # original_page

    class Meta:
        verbose_name = "Proyecto Final en la Cuenta Publica"
        verbose_name_plural = "Proyectos Finales en la Cuenta Publica"

    def __unicode__(self):
        return self.project
