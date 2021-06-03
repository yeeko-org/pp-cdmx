# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from classification.models import CategoryOllin

from django.db import models

from geographic.models import TownHall

from period.models import PeriodPP

from project.models import FinalProject

from .pp_image_mixins.config_mix import PPImageMix
from .pp_image_mixins.data_processing_mix import PPImageDataProcessingMix
from .pp_image_mixins.old_mix import PPImageOldMix
from .pp_image_mixins.references_mix import PPImageReferencesMix
from .pp_image_mixins.vision_mix import PPImageVisionMix

from .public_account_mixins.cleaner_mix import PublicAccountCleanerMix
from .public_account_mixins.config_mix import PublicAccountMix
from .public_account_mixins.match_mix import PublicAccountMatchMix
from .public_account_mixins.old_mix import PublicAccountOldMix
from .public_account_mixins.vision_mix import PublicAccountVisionMix


class PublicAccount(models.Model, PublicAccountCleanerMix,
                    PublicAccountMatchMix, PublicAccountMix,
                    PublicAccountOldMix, PublicAccountVisionMix):

    VERTICAL_ALIGN_AMMOUNTS = (
        ("top", u"top"),
        ("center", u"center"),
        ("bottom", u"bottom"),
    )
    UNREADABLE = (
        ("bajo", u"bajo"),
        ("media", u"media"),
        ("alto", u"alto"),
    )
    townhall = models.ForeignKey(
        TownHall,
        blank=True,
        null=True,
        verbose_name=u"Alcaldía")
    period_pp = models.ForeignKey(PeriodPP, verbose_name=u"Periodo PP")
    variables = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=80, default=u"uncleaned",
        blank=True, null=True)
    error_cell = models.TextField(
        blank=True, null=True,
        verbose_name="pila de errores")
    orphan_rows = models.TextField(
        blank=True, null=True,
        verbose_name="Filas no insertadas")

    approved = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True,
        verbose_name=u"Aprobado")

    assigned = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True,
        verbose_name=u"Asignado")

    modified = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True,
        verbose_name=u"Modificado")
    executed = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True,
        verbose_name=u"Ejecutado")

    vertical_align_ammounts = models.CharField(
        choices=VERTICAL_ALIGN_AMMOUNTS,
        max_length=50,
        blank=True, null=True)

    unreadable = models.CharField(
        choices=UNREADABLE, max_length=50,
        verbose_name="Nivel de ilegibilidad",
        blank=True, null=True)

    ignore_columns = models.CharField(
        max_length=50,
        help_text=u"columnas a ignorar para la alineacion horizontal (4-8)",
        blank=True, null=True)

    approved_mean = models.FloatField(blank=True, null=True)
    executed_mean = models.FloatField(blank=True, null=True)

    not_executed = models.IntegerField(blank=True, null=True)
    minus_10 = models.IntegerField(blank=True, null=True)
    minus_5 = models.IntegerField(blank=True, null=True)
    similar = models.IntegerField(blank=True, null=True)
    plus_5 = models.IntegerField(blank=True, null=True)

    no_info = models.NullBooleanField(blank=True, null=True)

    match_review = models.NullBooleanField(blank=True, null=True)
    suburb_count = models.IntegerField(blank=True, null=True)
    manual_mach = models.TextField(blank=True, null=True)
    comment_match = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u"%s -- %s" % (self.period_pp, self.townhall)

    class Meta:
        verbose_name = u"Cuenta Publica"
        verbose_name_plural = u"Cuentas Publicas"


class PPImage(models.Model, PPImageMix,
              PPImageDataProcessingMix, PPImageOldMix,
              PPImageReferencesMix, PPImageVisionMix):
    public_account = models.ForeignKey(
        PublicAccount, related_name=u"pp_images")
    path = models.CharField(max_length=255)
    json_variables = models.TextField(blank=True, null=True)

    headers = models.TextField(blank=True, null=True)
    table_data = models.TextField(blank=True, null=True)
    first_headers_used = models.BooleanField(default=True)

    vision_data = models.TextField(blank=True, null=True)
    clean_data = models.TextField(blank=True, null=True)
    error_cell = models.TextField(
        blank=True, null=True, verbose_name="pila de errores")
    len_array_numbers = models.CharField(
        max_length=80, blank=True, null=True)
    data_row_numbers = models.TextField(
        blank=True, null=True, verbose_name=u"Datos de columnas numéricas")
    data_row_suburbs = models.TextField(
        blank=True, null=True, verbose_name=u"Datos de columna de suburbs")
    status = models.CharField(
        blank=True, null=True, max_length=80, default=u"uncleaned")

    need_manual_ref = models.NullBooleanField(blank=True, null=True)
    manual_ref = models.TextField(blank=True, null=True)

    need_second_manual_ref = models.NullBooleanField(blank=True, null=True)

    validated = models.NullBooleanField(blank=True, null=True)

    table_ref = models.TextField(
        verbose_name=u"Referencia de filas",
        blank=True, null=True,)
    table_ref_columns = models.TextField(
        verbose_name=u"Referencias de Columnas",
        blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u"%s %s %s" % (self.public_account, self.path, self.id or None)

    class Meta:
        verbose_name = u"Imagen de Cuenta Publica"
        verbose_name_plural = u"Imagenes de Cuentas Publicas"


class Row(models.Model):
    final_project = models.ForeignKey(
        FinalProject, blank=True, null=True, related_name=u"rows")
    image = models.ForeignKey(PPImage)
    project_name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    similar_suburb_name = models.DecimalField(
        max_digits=3, decimal_places=2, default=0, blank=True, null=True,
        verbose_name=u"Nivel de similitud de nombre (-1 cuando es forzado)")
    progress = models.DecimalField(
        max_digits=7, decimal_places=3,
        blank=True, null=True, verbose_name=u"Avance del proyecto")
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
    variation = models.DecimalField(
        max_digits=7, decimal_places=3,
        blank=True, null=True, verbose_name=u"Variacion")

    validated = models.NullBooleanField(
        verbose_name=u"Validado",
        blank=True, null=True)

    variation_calc = models.FloatField(blank=True, null=True)
    range = models.CharField(max_length=50, blank=True, null=True)

    errors = models.TextField(blank=True, null=True)
    sequential = models.SmallIntegerField(blank=True, null=True)
    vision_blocks = models.TextField(blank=True, null=True)
    vision_data = models.TextField(blank=True, null=True)
    formatted_data = models.TextField(blank=True, null=True)
    top = models.SmallIntegerField(blank=True, null=True)
    bottom = models.SmallIntegerField(blank=True, null=True)

    category = models.ForeignKey(CategoryOllin, blank=True, null=True)

    def get_vision_data(self, *args, **kwargs):
        try:
            return json.loads(self.vision_data)
        except Exception:
            return []

    def get_errors(self, *args, **kwargs):
        try:
            return json.loads(self.errors)
        except Exception:
            return []

    def set_errors(self, *args, **kwargs):
        if len(args) == 1:
            error = args[0]
        elif "error" in kwargs:
            error = kwargs["error"]
        else:
            return
        errors = self.get_errors()
        if error in errors:
            return
        errors.append(u"%s" % error)
        errors_unique = []
        for error in errors:
            if error in errors_unique:
                continue
            errors_unique.append(error)
        self.errors = json.dumps(errors)
        if kwargs.get("save", True):
            super(Row, self).save()

    def get_formatted_data(self, *args, **kwargs):
        try:
            return json.loads(self.formatted_data)
        except Exception:
            return []

    def calculate_category(self, category_value_min=80):
        row_category_list = []
        best_row_category = None
        RowCategory.objects.filter(row=self).delete()
        for category in CategoryOllin.objects.all():
            evaluation_text = u"%s %s" % (self.project_name, self.description)
            category_value = category.calculate_value(evaluation_text)
            if category_value >= category_value_min:
                row_category = RowCategory.objects\
                    .create(row=self, category=category)
                row_category.value = category_value
                row_category.save()
                row_category_list.append(row_category)
        if len(row_category_list) == 1:
            best_row_category = row_category_list[0]
        elif len(row_category_list) > 1:
            def category_value(obj):
                return obj.value
            row_category_list.sort(key=category_value, reverse=True)
            if row_category_list[0].value - 100 > row_category_list[1].value:
                best_row_category = row_category_list[0]

        if best_row_category:
            self.category = best_row_category.category
            self.save()

    def save(self, *args, **kwargs):
        if self.executed and self.approved:
            self.variation_calc = float((self.executed / self.approved) * 100)

            if self.variation_calc > 0 and self.variation_calc < 90:
                self.set_errors(u"Posible inconsistencia de montos", save=False)
            elif self.variation_calc > 110:
                self.set_errors(u"Aprobado muy alto", save=False)

            if self.variation_calc > 102.5:
                self.range = u">2.5%"

            elif self.variation_calc > 97.5:
                self.range = u"similar"

            elif self.variation_calc > 90:
                self.range = u"<-2.5%"

            elif self.variation_calc > 0:
                self.range = u"<-10%"

            else:
                self.range = u"not_executed"
                self.variation_calc = 0

        if self.progress:
            if self.progress > 1 or (
                    self.progress > 0 and self.progress < 0.8):
                self.set_errors(
                    u"Valor en columna Avance anormal", save=False)
        super(Row, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Row"
        verbose_name_plural = "Rows"

    def __unicode__(self):
        return u"%s - %s" % (self.image, self.sequential)


class RowCategory(models.Model):
    row = models.ForeignKey(Row, related_name=u"atl_categories")
    category = models.ForeignKey(CategoryOllin, null=True)
    value = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name = "RowCategory"
        verbose_name_plural = "RowCategorys"

    def __unicode__(self):
        return u"%s %s %s" % (self.row, self.category, self.value)
