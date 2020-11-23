# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from ckeditor.fields import RichTextField


class LawPP(models.Model):
    publish_year = models.IntegerField(verbose_name=u"Año de publicacion")
    name = models.TextField(verbose_name=u"Nombre")
    file_law = models.FileField(
        upload_to="law_pp",
        blank=True,
        null=True,
        verbose_name=u"Archivo de Ley")
    summary = RichTextField(blank=True, null=True, verbose_name=u"Contenido")

    class Meta:
        verbose_name = u"Ley Reglamentaria del Presupuesto Participativo"
        verbose_name_plural = (u"Leyes Reglamentarias del "
                               "Presupuesto Participativo")

    def __unicode__(self):
        return self.name


class PeriodPP(models.Model):
    year = models.IntegerField(verbose_name=u"Año")
    is_public = models.BooleanField(
        default=False, verbose_name=u"Es Publico")
    law_pp = models.ForeignKey(
        LawPP,
        blank=True,
        null=True,
        verbose_name=u"Ley Reglamentaria del PP")
    pdf_iecm = models.FileField(
        blank=True,
        null=True,
        upload_to="period_pp",
        verbose_name=u"Archivo PDF del IECM")

    # Formato estandar por año, detalles para la busqueda de referencias
    logo = models.CharField(
        max_length=100,
        default="gobierno de la ciudad de mexico; ciudad de mexico",
        blank=True, null=True)
    unidad = models.CharField(
        max_length=100, default="unidad responsable del gasto",
        blank=True, null=True)
    title = models.CharField(
        max_length=100, default="cuenta publica de la ciudad de mexico",
        blank=True, null=True)
    ppd = models.CharField(
        max_length=100,
        default="ppd presupuesto participativo para las delegaciones",
        blank=True, null=True)
    ammounts = models.CharField(
        max_length=100, default="presupuesto (pesos con dos decimales",
        blank=True, null=True)
    # headers
    colonia = models.CharField(
        max_length=100, default=u"colonia o pueblo originario",
        blank=True, null=True)
    proyecto = models.CharField(
        max_length=100, default=u"proyecto",
        blank=True, null=True)
    descripcion = models.CharField(
        max_length=100, default=u"descripción",
        blank=True, null=True)
    avance = models.CharField(
        max_length=100, default=u"avance del proyecto; del proyecto",
        blank=True, null=True)
    aprobado = models.CharField(
        max_length=100, default=u"aprobado",
        blank=True, null=True)
    modificado = models.CharField(
        max_length=100, default=u"modificado",
        blank=True, null=True)
    ejercido = models.CharField(
        max_length=100, default=u"ejercido",
        blank=True, null=True)
    variacion = models.CharField(
        max_length=100, default=u"variación",
        blank=True, null=True)

    def test_references(self, reset=False, main_only=True):
        from public_account.models import PPImage
        image_query = PPImage.objects.filter(public_account__period_pp=self)
        if reset:
            image_query.update(json_variables=None)
        if main_only:
            image_query = image_query.filter(path__icontains="0001")

        image_query = image_query.objects.exclude(
            public_account__unreadable__in=[u"alto"])

        audit_ref = {
            "total_images": image_query.count(),
            "logo": 0,
            "unidad": 0,
            "title": 0,
            "ppd": 0,
            "ammounts": 0,
            "colonia": 0,
            "proyecto": 0,
            "descripcion": 0,
            "avance": 0,
            "aprobado": 0,
            "modificado": 0,
            "ejercido": 0,
            "variacion": 0,
        }

        for image in image_query:
            image.find_reference_blocks()
            check_reference = image.check_reference()

            audit_ref["logo"] += check_reference.get("logo")
            audit_ref["unidad"] += check_reference.get("unidad")
            audit_ref["title"] += check_reference.get("title")
            audit_ref["ppd"] += check_reference.get("ppd")
            audit_ref["ammounts"] += check_reference.get("ammounts")
            audit_ref["colonia"] += check_reference.get("colonia")
            audit_ref["proyecto"] += check_reference.get("proyecto")
            audit_ref["descripcion"] += check_reference.get("descripcion")
            audit_ref["avance"] += check_reference.get("avance")
            audit_ref["aprobado"] += check_reference.get("aprobado")
            audit_ref["modificado"] += check_reference.get("modificado")
            audit_ref["ejercido"] += check_reference.get("ejercido")
            audit_ref["variacion"] += check_reference.get("variacion")
        return audit_ref

    def images_without_reference(self, reference, main_only=True):
        from public_account.models import PPImage
        image_query = PPImage.objects.filter(public_account__period_pp=self)
        images_reference = []
        if main_only:
            image_query = image_query.filter(path__icontains="0001")

        for image in image_query:
            check_reference = image.check_reference()
            if not check_reference.get(reference):
                images_reference.append(image)

        return images_reference

    def process_all_accounts(self, reset=True):
        from public_account.models import PublicAccount
        for public_account in PublicAccount.objects.filter(period_pp=self):
            public_account.column_formatter_v2(reset=reset)

    class Meta:
        verbose_name = u"Periodo de Presupuesto Participativo"
        verbose_name_plural = u"Periodos de Presupuesto Participativo"

    def __unicode__(self):
        return unicode(self.year)
