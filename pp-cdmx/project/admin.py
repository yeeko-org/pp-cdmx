# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Project, FinalProject


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    list_display = [
        "suburb", "period_pp", "name_iedf", "project_id", "category_iedf",
        "votes", "is_winer"]
    raw_id_fields = ["suburb", "period_pp", "category_iedf"]
admin.site.register(Project, ProjectAdmin)


class FinalProjectAdmin(admin.ModelAdmin):
    model = FinalProject
    list_display = [
        "suburb", "period_pp", "project", "total_votes", "description_cp"]
    fieldsets = [
        [None, {
            "fields": [
                "suburb", "period_pp", "project", "total_votes",
                "description_cp", "final_name", "category_cp"
            ]
        }],
        ["Ammounts", {
            #"classes": ["collapse"],
            "fields": [
                "assigned", "approuved", "modified", "excecuted", "progress"
            ]
        }],
        ["Observations", {
            #"classes": ["collapse"],
            "fields": [
                "observation", "validated", "user_validation"
            ]
        }]
    ]
    raw_id_fields = ["suburb", "period_pp", "project", "user_validation"]
admin.site.register(FinalProject, FinalProjectAdmin)
