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
    readonly_fields = ["get_image_url"]
    fieldsets = [
        [None, {
            "fields": [
                "public_account",
                "get_image_url",
                "table_data",
                "status",
                "need_manual_ref",
                "manual_ref",
            ]
        }],
        ["config", {
            "classes": ["collapse"],
            "fields": [
                "json_variables",
                "headers",
                "first_headers_used",
                "vision_data",
                "clean_data",
                "error_cell",
                "len_array_numbers",
                "data_row_numbers",
                "data_row_suburbs",
            ],
        }],
    ]

    def get_image_url(self, obj):
        from django.conf import settings as dj_settings
        from django.utils.html import format_html
        domain = getattr(dj_settings, "URL_NEXT_SERVER", "")
        full_url = u"%s%s/%s" % (
            domain,
            obj.public_account.period_pp.year,
            obj.path)
        return format_html('<a href="%s" target="_blank"><img src="%s" alt="image" width="500" height="400"></a><br>' % (
            full_url, full_url))

admin.site.register(PPImage, PPImageAdmin)
