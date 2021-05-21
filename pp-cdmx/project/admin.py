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
    raw_id_fields = ["suburb", "period_pp", "category_iecm"]
    list_filter = ["suburb__townhall", "category_iecm"]
    search_fields = [
        "suburb__name", "suburb__townhall__name",
        "category_iecm__name", "name_iecm"]
admin.site.register(Project, ProjectAdmin)


class FinalProjectAdmin(admin.ModelAdmin):
    model = FinalProject
    search_fields = [
        "suburb__name", "suburb__townhall__name", "suburb__cve_col",
        "anomalyfinalproject__anomaly__name"]
    # list_display = [
    #     "suburb", "period_pp", "project", "total_votes", "description_cp",
    #     "display_anomalyfinalprojectinline"]
    list_display = [
        "suburb", "period_pp", "project",
        "assigned",
        "approved",
        "modified",
        "executed",
        "progress",
        "variation",
    ]
    list_filter = ["suburb__townhall", "anomalyfinalproject__anomaly",
                   "period_pp"]
    fieldsets = [
        [None, {
            "fields": [
                "suburb", "period_pp", "project", "total_votes",
                "description_cp", "final_name"  # , "category_cp"
            ]
        }],
        ["Ammounts", {
            "classes": ["collapse"],
            "fields": [
                "progress",  # "approuved",
                "approved",  # "excecuted",
                "modified",  # "excecuted",
                "executed",  # "excecuted",
                "variation"  # "excecuted",
            ]
        }],
        ["Observations", {
            "classes": ["collapse"],
            "fields": [
                "observation", "validated", "user_validation",
                "manual_capture", "pre_clasification"
            ]
        }],
        ["Procesados de Google Vision", {
            "classes": ["collapse"],
            "fields": [
                "image", "similar_suburb_name", "name_in_pa",
                "json_variables", "error_cell", "inserted_data",
                "data_raw"
            ]
        }]
    ]
    inlines = [AnomalyFinalProjectInline]
    raw_id_fields = [
        "suburb", "period_pp", "project", "user_validation"
    ]

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
