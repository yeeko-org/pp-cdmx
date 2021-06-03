# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from classification.models import Anomaly, CategoryIECM

from django.contrib.auth.models import User
from django.db import models

from geographic.models import Suburb

from period.models import PeriodPP


class Project(models.Model):
    """Esta clase es para algo."""

    suburb = models.ForeignKey(Suburb, verbose_name=u"Colonia")
    period_pp = models.ForeignKey(PeriodPP, verbose_name=u"Periodo PP")
    # name_iecm = models.CharField(
    #     blank=True, null=True,
    #     max_length=255,
    #     verbose_name=u"Nombre del IECM")
    name_iecm = models.TextField(
        blank=True, null=True,
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
    is_winner = models.BooleanField(
        default=False, verbose_name=u"Es el ganador")

    class Meta:
        verbose_name = "Proyecto de Presupuesto"
        verbose_name_plural = "Proyectos de Presupuestos"
        ordering = ["-votes"]

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
    image = models.IntegerField(blank=True, null=True)
    similar_suburb_name = models.DecimalField(
        max_digits=3, decimal_places=2, default=0, blank=True, null=True,
        verbose_name=u"Nivel de similitud de nombre (-1 cuando es forzado)")
    name_in_pa = models.CharField(
        max_length=140, blank=True, null=True,
        verbose_name=u"Nombre como aparece en cuenta pública")
    json_variables = models.TextField(
        blank=True, null=True,
        verbose_name=u"Variables originales de su columna")
    error_cell = models.TextField(blank=True, null=True,
                                  verbose_name=u"pila de errores")
    inserted_data = models.BooleanField(
        default=False, verbose_name=u"Datos insertados desde cuenta pública")

    data_raw = models.TextField(blank=True, null=True,
                                verbose_name=u"Informacion de la imagen")

    variation_calc = models.FloatField(blank=True, null=True)

    range = models.CharField(max_length=50, blank=True, null=True)

    votes_int = models.SmallIntegerField(blank=True, null=True)

    # pre_clasification
    # manuela_
    # original_page

    def get_data_raw(self):
        try:
            return json.loads(self.data_raw)
        except Exception:
            return None

    def set_data_raw(self, data):
        try:
            self.data_raw = json.dumps(data)
        except Exception:
            self.data_raw = None

    def get_json_variables(self):
        try:
            return json.loads(self.json_variables)
        except Exception:
            return None

    def set_json_variables(self, data):
        try:
            self.json_variables = json.dumps(data)
        except Exception:
            self.json_variables = None

    def projects(self):
        return Project.objects\
            .filter(suburb=self.suburb, period_pp=self.period_pp)\
            .distinct()

    def get_first_row(self):
        # colocar algo mas complejo como ordenarlos por el valor de la relacion
        from public_account.models import Row
        return Row.objects.filter(final_project=self).first()

    def check_project_winner(self):
        # from scripts.data_cleaner_v2 import similar
        self.remove_anomaly([
            u"Ganador y ejecutado distintos",
            u"Sin ganador y ejecutado",
            u"Nombre del Proyecto IECM no coincidente"
        ])

        print self
        project_query = Project.objects.filter(
            period_pp=self.period_pp, is_winner=True)
        project_count = project_query.count()
        winner_project = None
        anomaly_text = None
        anomaly_is_public = None
        if project_count == 1:
            # un solo ganador
            winner_project = project_query.first()
            if not check_names(winner_project, self,
                               similar_value_min=0.85):
                # el ganador no es el mismo que el registrado, buscar posible
                # ganador
                winner_project = find_winner(
                    Project.objects.filter(
                        period_pp=self.period_pp),
                    self, 0.7)
                anomaly_text = "Ganador y ejecutado distintos"
        elif project_count:
            # multiples ganadores
            winner_project = find_winner(
                Project.objects.filter(
                    period_pp=self.period_pp, is_winner=True),
                self, 0.7)
            if not winner_project:
                winner_project = find_winner(
                    Project.objects.filter(
                        period_pp=self.period_pp),
                    self, 0.7)
                anomaly_text = "Ganador y ejecutado distintos"
        else:
            winner_project = find_winner(
                Project.objects.filter(
                    period_pp=self.period_pp),
                self, 0.7)
            anomaly_text = "Sin ganador y ejecutado"
        if not winner_project:
            anomaly_text = "Nombre del Proyecto IECM no coincidente"
            anomaly_is_public = False
        else:
            self.project = winner_project
        if anomaly_text:
            self.set_anomaly(anomaly_text, anomaly_is_public=anomaly_is_public)
            print anomaly_text
        print self.project
        print

    def calculate_winner(self):
        from django.db.models import Max, Sum
        project_fp_year_query = Project.objects\
            .filter(suburb=self.suburb,
                    period_pp=self.period_pp)

        # Cuando no se encuentre ningún Project asociado al FinalProject
        if not project_fp_year_query.exists():
            self.set_anomaly("Sin proyectos presentados")
            print self.id, u": ", self
            return

        votes__max = project_fp_year_query\
            .aggregate(Max('votes')).get("votes__max")
        votes__sum = project_fp_year_query\
            .aggregate(Sum('votes')).get("votes__sum")
        votes_int__sum = project_fp_year_query\
            .aggregate(Sum('votes_int')).get("votes_int__sum")

        self.total_votes = votes__sum
        self.votes_int = votes_int__sum
        self.save()
        winner_proyects_list = []

        # Si FinalProject.votes_int / FinalProject.total_votes >= 0.2
        if (self.votes_int / self.total_votes) >= 0.2:
            self.set_anomaly("Demasiados votos por internet")
        # Cuando el Project o los Projects ganadores tienen menos de 5 votos
        if votes__max < 5:
            self.set_anomaly("Ganador con menos de 5 votos")
        # Si FinalProject.total_votes == 0
        if not self.total_votes:
            self.set_anomaly("Sin votos")
        # "Un solo proyecto presentado": Cuando solo se encuentre un Project asociado al FinalProject
        if project_fp_year_query.count() == 1:
            self.set_anomaly("Un solo proyecto presentado")

        if votes__max:
            winner_proyects = project_fp_year_query\
                .filter(votes=votes__max)
            count_winners = winner_proyects.count()

            if not count_winners:
                self.set_anomaly("No hay proyecto ganador")
            else:
                winner_proyects.update(is_winner=True)
                winner_proyects_list = winner_proyects.values_list(
                    "suburb__short_name", flat=True)

            if count_winners > 1:
                self.set_anomaly(u"Empate de votos")
        else:
            # sin proyecto ganador
            count_winners = 0

        print "%s | %s | %s" % (
            self.suburb.cve_col,
            self.suburb.name,
            self.suburb.townhall.name)
        print "votes__max: %s" % votes__max
        print "votes__sum: %s" % votes__sum
        print "final_project: %s" % self
        print "winner_proyects: %s" % winner_proyects_list
        print "count_winners: %s" % count_winners
        print

    def set_anomaly(self, name, is_public=True):
        anomaly, is_created = Anomaly.objects\
            .get_or_create(name=name)
        if is_public is False:
            anomaly.is_public = False
            anomaly.save()
        anomaly_fp, is_created = AnomalyFinalProject.objects\
            .get_or_create(anomaly=anomaly, final_project=self)

    def remove_anomaly(self, anomaly_name):
        if isinstance(anomaly_name, list):
            AnomalyFinalProject.objects\
                .filter(anomaly__name__in=anomaly_name, final_project=self)\
                .delete()

        AnomalyFinalProject.objects\
            .filter(anomaly__name=anomaly_name, final_project=self).delete()

    class Meta:
        verbose_name = "Proyecto Final en la Cuenta Publica"
        verbose_name_plural = "Proyectos Finales en la Cuenta Publica"

    def __unicode__(self):
        return u"%s - %s" % (self.suburb, self.period_pp)


class AnomalyFinalProject(models.Model):
    anomaly = models.ForeignKey(Anomaly)
    final_project = models.ForeignKey(FinalProject, blank=True, null=True)

    def __unicode__(self):
        return u"%s -%s" % (self.final_project or self.public_account,
                            self.anomaly)

    class Meta:
        verbose_name_plural = u"Anomalía y Proyecto Final"
        verbose_name = u"Anomalía y Proyecto Final"


def check_names(winner_project, final_project, similar_value_min=0.85):
    from scripts.data_cleaner_v2 import similar
    row = final_project.get_first_row()
    if not row:
        return 0
    winner_project_name_iecm = (winner_project.name_iecm or "").lower().strip()
    row_project_name = (row.project_name or "").lower().strip()
    row_description = (row.description or "").lower().strip()
    similar_value1 = similar(
        winner_project_name_iecm,
        row_project_name)
    similar_value2 = similar(
        winner_project_name_iecm,
        row_description)
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


def find_winner(project_query, final_project, similar_value_min):
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
