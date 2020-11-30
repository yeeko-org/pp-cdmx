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

    global_error_stack = models.TextField(blank=True, null=True)
    all_results = models.TextField(blank=True, null=True)

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

    # Primero creamos todos los proyectos finales de un año determinado
    def create_final_project(self):
        from geographic.models import Suburb
        from project.models import FinalProject
        all_suburbs = Suburb.objects.all()
        for sub in all_suburbs:
            finalproject, is_created = FinalProject.objects\
                .get_or_create(period_pp=self, suburb=sub)
        # comprobamos los 1812 proyectos finales:
        all_final = FinalProject.objects.all()
        print all_final.count()

    def print_all_results(self):
        from project.models import FinalProject
        from geographic.models import TownHall
        results=[]
        for th in TownHall.objects.all():
            results.append(print_results(self, th))
        results.append(print_results(self))
        self.all_results=u"\n".join(results)
        self.save()
        print self.all_results

    def test_references(self, reset=False, main_only=True):
        from public_account.models import PPImage
        image_query = PPImage.objects.filter(public_account__period_pp=self)
        if reset:
            image_query.update(json_variables=None)
        if main_only:
            image_query = image_query.filter(path__icontains="0001")

        image_query = image_query.exclude(
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
        if reset or not self.global_error_stack:
            self.global_error_stack = ""
        for public_account in PublicAccount.objects.filter(period_pp=self):
            public_account.column_formatter_v2(reset=reset)
            self.global_error_stack = u"\n".join([
                self.global_error_stack, public_account.error_cell or ""])
        self.save()
        self.print_all_results()

    class Meta:
        verbose_name = u"Periodo de Presupuesto Participativo"
        verbose_name_plural = u"Periodos de Presupuesto Participativo"

    def __unicode__(self):
        return unicode(self.year)


def result_percent(res_count, total, type_res):
    base_count = float(total) / 100
    return "%s  -->  %s%s %s" % (
        res_count, round(res_count / base_count, 1), "%", type_res)


def print_results(year=2018, th=None):
    from project.models import FinalProject
    results = ["*********************"]
    results.append(th.name if th else 'RESULTADOS GLOBALES')
    base_fp = FinalProject.objects.filter(period_pp=year)
    if th:
        base_fp = base_fp.filter(suburb__townhall=th)
    base_count = base_fp.count()
    results.append("%s  --> TOTAL" % base_count)
    linked_sub = base_fp.filter(image__isnull=False)
    complete_sub = linked_sub.filter(
        approved__isnull=False, modified__isnull=False,
        executed__isnull=False, progress__isnull=False)
    without_error = complete_sub.exclude(
        anomalyfinalproject__isnull=False,
        anomalyfinalproject__anomaly__is_public=False)
    results.append(result_percent(linked_sub.count(),
                                  base_count, 'vinculados'))
    results.append(result_percent(complete_sub.count(),
                                  base_count, 'completos'))
    results.append(result_percent(without_error.count(),
                                  base_count, 'sin errores'))
    return u"\n".join(results)
