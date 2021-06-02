# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Anomaly, CategoryIECM, CategoryOllin


admin.site.register(CategoryIECM)


class AnomalyAdmin(admin.ModelAdmin):
    model = Anomaly
    list_display = ["name", "is_public"]
    list_filter = ["is_public"]
admin.site.register(Anomaly, AnomalyAdmin)


class CategoryOllinAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "public_name",
        "description",
        "develop_community",
        "dictionary_values"]
    list_editable = ["develop_community", "dictionary_values"]

admin.site.register(CategoryOllin, CategoryOllinAdmin)
