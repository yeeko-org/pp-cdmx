# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import (
    TownHall, TownHallGeoData, SuburbType, Suburb, SuburbGeoData)


class TownHallGeoDataInline(admin.StackedInline):
    model = TownHallGeoData


class TownHallAdmin(admin.ModelAdmin):
    model = TownHall
    list_display = [
        "cve_inegi", "cve_alc", "name", "short_name", "image"]
    inlines = [TownHallGeoDataInline]
admin.site.register(TownHall, TownHallAdmin)


class SuburbTypeAdmin(admin.ModelAdmin):
    model = SuburbType
    list_display = [
        "name", "abrev", "icon", "emoji"]
admin.site.register(SuburbType, SuburbTypeAdmin)


class SuburbGeoDataInline(admin.StackedInline):
    model = SuburbGeoData


class SuburbAdmin(admin.ModelAdmin):
    model = Suburb
    list_display = [
        "cve_col", "name", "short_name", "townhall",
        "suburb_type", "is_pilot"]
    list_filter = ["townhall", "suburb_type"]
    raw_id_fields = ["townhall", "suburb_type", "derivation_suburb"]
    inlines = [SuburbGeoDataInline]
admin.site.register(Suburb, SuburbAdmin)
