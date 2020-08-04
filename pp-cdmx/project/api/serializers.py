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

    class Meta:
        model = FinalProject
        fields = [
            "suburb",
            "total_votes",
            "final_name",
            "assigned",
            "executed",
            "progress",
        ]
        # depth = 2
