# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Project, FinalProject, AnomalyFinalProject


class AnomalyFinalProjectInline(admin.TabularInline):
    model = AnomalyFinalProject
    show_change_link = True
    extra = 0
    raw_id_fields = ["anomaly"]
    #classes = ['collapse']


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    list_display = [
        "suburb", "period_pp", "name_iecm", "project_id", "category_iecm",
        "votes", "is_winer"]
    raw_id_fields = ["suburb", "period_pp", "category_iecm"
                     ]
admin.site.register(Project, ProjectAdmin)


class FinalProjectAdmin(admin.ModelAdmin):
    model = FinalProject
    list_display = [
        "suburb", "period_pp", "project", "total_votes", "description_cp", "display_anomalyfinalprojectinline"]
    fieldsets = [
        [None, {
            "fields": [
                "suburb", "period_pp", "project", "total_votes",
                "description_cp", "final_name", "category_cp"
            ]
        }],
        ["Ammounts", {
            "classes": ["collapse"],
            "fields": [
                "assigned", "approuved", "modified", "excecuted", "progress"
            ]
        }],
        ["Observations", {
            "classes": ["collapse"],
            "fields": [
                "observation", "validated", "user_validation"
            ]
        }]
    ]
    inlines = [AnomalyFinalProjectInline]
    raw_id_fields = ["suburb", "period_pp", "project", "user_validation"]

    def display_anomalyfinalprojectinline(self, obj):
        from django.utils.html import format_html
        from classification.models import Anomaly
        anomaly_query = Anomaly.objects\
            .filter(anomalyfinalproject__final_project=obj)\
            .values_list("name", flat=True)\
            .distinct()
        return format_html("<br>".join(anomaly_query))
    display_anomalyfinalprojectinline.short_description = "Anomalías"
admin.site.register(FinalProject, FinalProjectAdmin)
