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
        "townhall", "period_pp", "status", "approved", "assigned", "modified",
        "executed", "vertical_align_ammounts", "unreadable"]
    # inlines = [PPImageInline]
    list_filter = ["townhall__name", "period_pp__year"]
    list_editable = [
        "approved", "assigned", "modified", "executed",
        "unreadable"]
    readonly_fields = ["vertical_align_ammounts"]
admin.site.register(PublicAccount, PublicAccountAdmin)


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
    raw_id_fields = ["public_account"]
    readonly_fields = ["get_image_url"]
    fieldsets = [
        [None, {
            "fields": [
                "public_account",
                "get_image_url",
                "table_data",
                "table_ref",
                "table_ref_columns",
                "status",
                "need_manual_ref",
                "manual_ref",
                "need_second_manual_ref",
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
