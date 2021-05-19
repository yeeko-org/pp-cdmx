# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from geographic.models import Suburb

from period.models import PeriodPP
from classification.models import CategoryIECM, Anomaly

from django.contrib.auth.models import User
from public_account.models import PPImage

from public_account.models import PublicAccount
import json


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
    votes_mro = models.IntegerField(default=0, verbose_name=u"Votos físicos")
    votes_int = models.IntegerField(default=0, verbose_name=u"Votos internet")
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
    final_name = models.TextField(
        blank=True,
        null=True,
        verbose_name=u"Nombre Final")
    description_cp = models.TextField(
        blank=True, null=True, verbose_name=u"Descripcion CP")
    project_cp = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=u"Proyecto CP")
    # category_ollin
    # subcategory

    # Ammounts
    # cambiar a decimal todos los float
    assigned = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True, verbose_name=u"Asignado")
    approved = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True, verbose_name=u"Aprobado")
    modified = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True,
        null=True,
        verbose_name=u"Modificado")
    executed = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True, verbose_name=u"Ejecutado")

    progress = models.FloatField(
        blank=True, null=True, verbose_name=u"Avance del proyecto")

    variation = models.FloatField(
        blank=True, null=True, verbose_name=u"Variacion")

    # Observations
    manual_capture = models.TextField(
        blank=True, null=True, verbose_name=u"Captura Manual")
    observation = models.TextField(
        blank=True, null=True, verbose_name=u"Observaciones")
    pre_clasification = models.TextField(
        blank=True, null=True, verbose_name=u"Pre-clasificación")
    validated = models.NullBooleanField(
        verbose_name=u"Validado",
        blank=True, null=True)
    user_validation = models.ForeignKey(
        User, blank=True, null=True, verbose_name=u"Usuario validador")

    # Variables from Vision
    image = models.ForeignKey(PPImage, blank=True, null=True)
    similar_suburb_name = models.DecimalField(
        max_digits=3, decimal_places=2, default=0, blank=True, null=True,
        verbose_name=u"Nivel de similitud de nombre (-1 cuando es forzado)")
    name_in_pa= models.CharField( max_length=140, blank=True, null=True,
        verbose_name=u"Nombre como aparece en cuenta pública")
    json_variables = models.TextField(blank=True, null=True, 
        verbose_name=u"Variables originales de su columna")
    error_cell = models.TextField(blank=True, null=True, 
        verbose_name=u"pila de errores")
    inserted_data = models.BooleanField(default=False, 
        verbose_name=u"Datos insertados desde cuenta pública")

    data_raw = models.TextField(blank=True, null=True, 
        verbose_name=u"Informacion de la imagen")
    
    variation_calc = models.FloatField(blank=True, null=True)

    range=models.CharField(max_length=50, blank=True, null=True)

    # pre_clasification
    # manuela_
    # original_page

    def get_data_raw(self):
        try:
            return json.loads(self.data_raw)
        except Exception as e:
            return None

    def set_data_raw(self, data):
        try:
            self.data_raw = json.dumps(data)
        except Exception as e:
            self.data_raw = None

    def get_json_variables(self):
        try:
            return json.loads(self.json_variables)
        except Exception as e:
            return None

    def set_json_variables(self, data):
        try:
            self.json_variables = json.dumps(data)
        except Exception as e:
            self.json_variables = None

    def projects(self):
        return Project.objects\
            .filter(suburb=self.suburb, period_pp=self.period_pp)\
            .distinct()

    def check_project_winer(self):
        from project.models import Project, FinalProject, AnomalyFinalProject
        from classification.models import Anomaly
        from scripts.data_cleaner_v2 import similar

        print self
        project_query = Project.objects.filter(
            period_pp=self.period_pp, is_winer=True)
        project_count = project_query.count()
        winer_project = None
        anomaly_text = None
        anomaly_is_public = None
        if project_count == 1:
            # un solo ganador
            winer_project = project_query.first()
            if not check_names(winer_project, self,
                               similar_value_min=0.85):
                # el ganador no es el mismo que el registrado, buscar posible
                # ganador
                winer_project = find_winer(
                    Project.objects.filter(
                        period_pp=self.period_pp),
                    self, 0.7)
                anomaly_text = "Ganador y ejecutado distintos"
        elif project_count:
            # multiples ganadores
            winer_project = find_winer(
                Project.objects.filter(
                    period_pp=self.period_pp, is_winer=True),
                self, 0.7)
            if not winer_project:
                winer_project = find_winer(
                    Project.objects.filter(
                        period_pp=self.period_pp),
                    self, 0.7)
                anomaly_text = "Ganador y ejecutado distintos"
        else:
            winer_project = find_winer(
                Project.objects.filter(
                    period_pp=self.period_pp),
                self, 0.7)
            anomaly_text = "Sin ganador y ejecutado"
        if not winer_project:
            anomaly_text = "Nombre del Proyecto IECM no coincidente"
            anomaly_is_public = False
        else:
            self.project=winer_project
        if anomaly_text:
            anomaly_obj, is_created = Anomaly.objects\
                .get_or_create(name=anomaly_text)
            if isinstance(anomaly_is_public, bool):
                anomaly_obj.is_public=anomaly_is_public
                anomaly_obj.save()
            anomaly_final_project, is_created=AnomalyFinalProject.objects\
                .get_or_create(
                    anomaly=anomaly_obj,
                    final_project=self,
                    )
            print anomaly_text
        print self.project
        print

    class Meta:
        verbose_name = "Proyecto Final en la Cuenta Publica"
        verbose_name_plural = "Proyectos Finales en la Cuenta Publica"

    def __unicode__(self):
        return u"%s - %s" % (self.suburb, self.period_pp)


class AnomalyFinalProject(models.Model):
    anomaly = models.ForeignKey(Anomaly)
    final_project = models.ForeignKey(FinalProject, blank=True, null=True)
    public_account = models.ForeignKey(PublicAccount, blank=True, null=True)

    def __unicode__(self):
        return u"%s -%s" % (self.final_project, self.anomaly)

    class Meta:
        verbose_name_plural = u"Anomalía y Proyecto Final"
        verbose_name = u"Anomalía y Proyecto Final"



def check_names(winer_project, final_project, similar_value_min=0.85):
    from scripts.data_cleaner_v2 import similar
    winer_project_name_iecm=(winer_project.name_iecm or "").lower().strip()
    final_project_final_name = (final_project.final_name or "").lower().strip()
    final_project_description_cp = (final_project.description_cp or "").lower().strip()
    similar_value1 = similar(
        winer_project_name_iecm,
        final_project_final_name)
    similar_value2 = similar(
        winer_project_name_iecm,
        final_project_description_cp)
    if similar_value1 > similar_value2:
        max_value = similar_value1
    else:
        max_value = similar_value2
    if max_value >= similar_value_min:
        return max_value
    else:
        return 0


def key_similar_value(block):
    return block["similar_value"]


def find_winer(project_query, final_project, similar_value_min):
    projects = []
    for project in project_query:
        similar_value = check_names(project, final_project, similar_value_min)
        if not similar_value:
            continue
        projects.append(
            {
                "project": project,
                "similar_value": similar_value
            }
        )
    if not projects:
        return None
    projects.sort(key=key_similar_value, reverse=True)
    return projects[0]["project"]


