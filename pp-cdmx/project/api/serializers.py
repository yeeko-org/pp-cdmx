# -*- coding: utf-8 -*-
from rest_framework import serializers

from project.models import (Project, FinalProject)


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
        ]
        # depth = 2
