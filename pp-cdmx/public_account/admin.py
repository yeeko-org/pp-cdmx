# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import PublicAccount, PPImage
from project.models import FinalProject


class PPImageInline(admin.StackedInline):
    model = PPImage
    extra = 0


class PublicAccountAdmin(admin.ModelAdmin):
    model = PublicAccount
    list_display = [
        "townhall", "period_pp", "status", "approved", "modified",
        "executed", "vertical_align_ammounts", "unreadable"]
    inlines = [PPImageInline]
    list_filter = ["townhall__name", "period_pp__year"]
    list_editable = [
        "approved", "modified", "executed", "vertical_align_ammounts",
        "unreadable"]
admin.site.register(PublicAccount, PublicAccountAdmin)


class FinalProjectInline(admin.StackedInline):
    model = FinalProject
    extra = 0
    raw_id_fields = ["suburb", "period_pp", "project", "user_validation"]
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
                "json_variables", "error_cell", "inserted_data"
            ]
        }]
    ]


class PPImageAdmin(admin.ModelAdmin):
    model = PPImage
    list_display = ["public_account", "path", "status", "len_array_numbers",
                    "error_cell"]
    list_filter = [
        "public_account__townhall",
        "public_account__period_pp__year"]
    search_fields = [
        "path", "public_account__townhall__name",
        "finalproject__suburb__name"]
    #inlines = [FinalProjectInline]
    raw_id_fields = ["public_account"]
admin.site.register(PPImage, PPImageAdmin)
