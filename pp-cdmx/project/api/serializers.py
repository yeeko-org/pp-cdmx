# -*- coding: utf-8 -*-
from rest_framework import serializers

from project.models import (Project, FinalProject, AnomalyFinalProject)


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = "__all__"
        # depth = 2


class FinalProjectSerializer(serializers.ModelSerializer):
    projects = ProjectSerializer(many=True)

    class Meta:
        model = FinalProject
        fields = [
            "suburb",
            "period_pp",
            "project",
            "total_votes",
            "description_cp",
            "project_cp",
            "final_name",
            "assigned",
            "approved",
            "modified",
            "executed",
            "progress",
            "manual_capture",
            "observation",
            "pre_clasification",
            "validated",
            "projects",
        ]
        # depth = 2


class FinalProjectSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = FinalProject
        fields = [
            "id",
            "final_name",
            "project_cp",
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
        read_only_fields = [
            "id",
            "final_name",
            "project_cp",
            "observation",
            "validated",
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

    project_name_iecm = serializers.ReadOnlyField(source="project.name_iecm")
    period_pp = serializers.ReadOnlyField(source="period_pp.year")

    class Meta:
        model = FinalProject
        fields = [
            "id",
            "suburb",
            "suburb_name",
            "suburb_short_name",
            "project",
            "project_name_iecm",
            "period_pp",
            "image",
        ]
        # depth = 2


class AnomalyFinalProjectSerializer(serializers.ModelSerializer):
    from classification.api.serializers import AnomalySerializer
    anomaly = AnomalySerializer()

    class Meta:
        model = AnomalyFinalProject
        fields = "__all__"
        # depth = 2

class FinalProjectRefsSerializer(serializers.ModelSerializer):
    suburb_name = serializers.ReadOnlyField(source="suburb.name")

    period_pp = serializers.ReadOnlyField(source="period_pp.year")
    data_raw = serializers.SerializerMethodField()
    def get_data_raw(self, obj):
        try:
            return obj.get_data_raw()
        except Exception as e:
            return None
    anomalies = serializers.SerializerMethodField()
    def get_anomalies(self, obj):
        try:
            anoms_fp = AnomalyFinalProject.objects.filter(final_project=obj, 
                    anomaly__is_public=False).exclude(anomaly__id=21)
            return AnomalyFinalProjectSerializer(anoms_fp,many=True).data
        except Exception as e:
            return None

    class Meta:
        model = FinalProject
        fields = [
            "id",
            "suburb",
            "suburb_name",
            "project",
            "period_pp",
            "description_cp",
            "project_cp",
            "final_name",
            "assigned",
            "approved",
            "modified",
            "executed",
            "variation",
            "progress",
            "validated",
            "variation_calc",
            "data_raw",
            "anomalies",
            "anomalies",
        ]



