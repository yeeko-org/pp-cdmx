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
        "townhall", "period_pp"]
    inlines = [PPImageInline]
admin.site.register(PublicAccount, PublicAccountAdmin)


class FinalProjectInline(admin.StackedInline):
    model = FinalProject
    extra = 0
    raw_id_fields = ["suburb", "period_pp", "project", "user_validation"]


class PPImageAdmin(admin.ModelAdmin):
    model = PPImage
    list_display = ["public_account", "path", "status"]
    list_filter = [
        "public_account__townhall",
        "public_account__period_pp__year"]
    search_fields = [
        "path", "public_account__townhall__name",
        "finalproject__suburb__name"]
    inlines = [FinalProjectInline]
    raw_id_fields = ["public_account"]
admin.site.register(PPImage, PPImageAdmin)
