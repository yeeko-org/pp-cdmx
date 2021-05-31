# -*- coding: utf-8 -*-
from rest_framework import serializers

from project.models import (Project, FinalProject, AnomalyFinalProject)


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = "__all__"
        # depth = 2


class AnomalyFinalProjectSerializer(serializers.ModelSerializer):
    from classification.api.serializers import AnomalySerializer
    anomaly = AnomalySerializer()

    class Meta:
        model = AnomalyFinalProject
        fields = "__all__"
        # depth = 2


class FinalProjectSerializer(serializers.ModelSerializer):
    from public_account.api.serializers import RowSerializer
    projects = ProjectSerializer(many=True)
    year = serializers.ReadOnlyField(source="period_pp.year", default=None)
    anomalies = serializers.SerializerMethodField()
    rows = RowSerializer(many=True)

    def get_anomalies(self, obj):
        from classification.api.serializers import AnomalySerializer
        from classification.models import Anomaly
        anomaly_query = Anomaly.objects.filter(
            anomalyfinalproject__final_project=obj).distinct()
        return AnomalySerializer(anomaly_query, many=True).data

    class Meta:
        model = FinalProject
        fields = [
            "id",
            "suburb",
            #"period_pp",
            "year",
            "project",
            "total_votes",
            "manual_capture",
            #"observation",
            #"pre_clasification",
            "projects",
            "rows",
            "anomalies",
        ]
        # depth = 2


class FinalProjectSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = FinalProject
        fields = [
            "id",
            "final_name",
            "observation",
            "validated",
            "suburb",
            "project",
            "description_cp",
            "progress",
            "approved",
            "modified",
            "executed",
            "variation",
        ]
        # depth = 2


class FinalProjectSmallSerializer(serializers.ModelSerializer):
    category_iecm = serializers.ReadOnlyField(
        source="project.category_iecm_id", default=None)

    class Meta:
        model = FinalProject
        fields = [
            "suburb",
            "total_votes",
            "final_name",
            "assigned",
            "executed",
            "progress",
            "category_iecm",
        ]
        # depth = 2


class FinalProjectOrphanSerializer(serializers.ModelSerializer):
    suburb_name = serializers.ReadOnlyField(source="suburb.name")
    suburb_short_name = serializers.ReadOnlyField(source="suburb.short_name")
    suburb_cve_col = serializers.ReadOnlyField(source="suburb.cve_col")

    #project_name_iecm = serializers.ReadOnlyField(source="project.name_iecm")
    period_pp = serializers.ReadOnlyField(source="period_pp.year")
    rows_count = serializers.SerializerMethodField()

    def get_rows_count(self, obj):
        from public_account.models import Row
        return Row.objects.filter(final_project=obj).count()

    class Meta:
        model = FinalProject
        fields = [
            "id",
            "suburb",
            "suburb_name",
            "suburb_short_name",
            "suburb_cve_col",
            #"project",
            #"project_name_iecm",
            "period_pp",
            "rows_count",
        ]
        # depth = 2


class FinalProjectRefsSerializer(serializers.ModelSerializer):
    suburb_name = serializers.ReadOnlyField(source="suburb.name")
    suburb_short_name = serializers.ReadOnlyField(source="suburb.short_name")
    #from geographic.api.serializers import TownHallSerializer
    #suburb = TownHallSerializer()

    period_pp = serializers.ReadOnlyField(source="period_pp.year")

    class Meta:
        model = FinalProject
        fields = [
            "id",
            "suburb",
            "suburb_name",
            "suburb_short_name",
            "project",
            "period_pp",
        ]
