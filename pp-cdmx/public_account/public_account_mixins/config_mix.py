# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from geographic.models import Suburb


class PublicAccountMix:

    # funciones de json Field del modelo
    def get_variables(self):
        import json
        try:
            return json.loads(self.variables)
        except Exception:
            # print("self.variables No JSON object could be decoded, "
            #       "se reiniciara a { }")
            return {}

    def get_manual_macth(self):
        try:
            return json.loads(self.manual_mach)
        except Exception:
            raise None

    def set_manual_macth(self, data):
        try:
            self.manual_mach = json.dumps(data)
        except Exception:
            self.manual_mach = None

    def get_orphan_rows(self):
        import json
        try:
            return json.loads(self.orphan_rows)
        except Exception:
            # print("self.orphan_rows No JSON object could be decoded, "
            #       "se reiniciara a []")
            return []

    def set_orphan_rows(self, data):
        import json
        try:
            self.orphan_rows = json.dumps(data)
        except Exception:
            self.orphan_rows = None

    # utilidades
    @property
    def final_project_query(self):
        from project.models import FinalProject
        if not hasattr(self, "_final_project_query"):
            self._final_project_query = FinalProject.objects.filter(
                suburb__townhall=self.townhall, period_pp=self.period_pp)
        return self._final_project_query

    def calculate_median(self, **kwargs):
        from numpy import median
        approved_list = self.final_project_query.filter(approved__gt=0)\
            .values_list("approved", flat=True)
        self.approved_median = median(approved_list)
        if kwargs.get("save", True):
            self.save()

    def calculate_means(self, **kwargs):
        from django.db.models import Avg, Count

        avgs = self.final_project_query.aggregate(
            Avg('approved'), Avg('executed'))
        self.approved_mean = avgs.get("approved__avg")
        self.executed_mean = avgs.get("executed__avg")

        counts_query = self.final_project_query.values("range")\
            .annotate(Count("range"))
        counts = {
            range_data.get("range"): range_data.get("range__count")
            for range_data in counts_query
        }

        self.not_reported = counts.get(u"not_reported", None)
        self.not_approved = counts.get(u"not_approved", None)
        self.not_executed = counts.get(u"not_executed", None)
        self.minus_10 = counts.get(u"<-10%", None)
        self.minus_5 = counts.get(u"<-2.5%", None)
        self.similar = counts.get(u"similar", None)
        self.plus_5 = counts.get(u">2.5%", None)

        self.calculate_median(save=False)

        if kwargs.get("save", True):
            self.save()

    def reset(self, all_images=None):
        from project.models import AnomalyFinalProject
        from public_account.models import PPImage

        # if all_images:
        #     final_project_query.filter(image__in=all_images)

        self.final_project_query.update(
            image=None, similar_suburb_name=None, error_cell="",
            inserted_data=False, approved=None, modified=None,
            executed=None, progress=None, variation=None)

        # Se eliminan las anomalías pasadas.
        # claves, columna
        AnomalyFinalProject.objects\
            .filter(
                final_project__in=self.final_project_query,
                anomaly__is_public=False)\
            .exclude(anomaly__name__icontains="IECM")\
            .delete()
        # AnomalyFinalProject.objects.filter(public_account=self).delete()

        PPImage.objects.filter(public_account=self)\
            .update(status=None, error_cell=None, len_array_numbers=None,
                    data_row_numbers=None, data_row_suburbs=None,
                    # json_variables=None, table_data=None, headers=None
                    )

        self.orphan_rows = None
        self.error_cell = ""
        self.status = None
        self.save()

    def check_ammounts(self):
        """
        Para aquellas Cuentas Públicas completas (sin missing_subs),
        ejecutar el siguiente script (ponlo en una función aparte):
        Hacer una suma de los campos approved, modified y executed de los
        FinalProyect y compararlo con los campos del mismo nombre del
        PublicAccount correspondiente. Si no coinciden, asociar el
        PublicAccount con la Anomalía "Totales no cuadran"
        """
        from project.models import FinalProject, AnomalyFinalProject
        from classification.models import Anomaly

        print self

        missings_subs = Suburb.objects.filter(
            townhall=self.townhall,
            finalproject__period_pp=self.period_pp,
            finalproject__image__isnull=True)
        if missings_subs.exists():
            # Esta cuenta publica todavia tiene Colonias perdidas
            return

        real_approved = 0
        real_modified = 0
        real_executed = 0
        for final_proyect in FinalProject.objects.filter(
                suburb__townhall=self.townhall,
                period_pp=self.period_pp):
            real_approved += final_proyect.approved or 0
            real_modified += final_proyect.modified or 0
            real_executed += final_proyect.executed or 0

        if any([self.approved != real_approved,
                self.modified != real_modified,
                self.executed != real_executed]):
            anomaly_text = "Totales no cuadran"
            print anomaly_text
            anomaly, is_created = Anomaly.objects\
                .get_or_create(name=anomaly_text, is_public=False)
            anomaly_final_project, is_created = AnomalyFinalProject.objects\
                .get_or_create(
                    anomaly=anomaly,
                    public_account=self,
                )
        print
