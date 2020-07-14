# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import (
    TownHall, TownHallGeoData, SuburbType, Suburb, SuburbGeoData)


class TownHallAdmin(admin.ModelAdmin):
    model = TownHall
    list_display = [
        "cve_inegi", "cve_alc", "name", "short_name", "image"]
admin.site.register(TownHall, TownHallAdmin)
admin.site.register(TownHallGeoData)


class SuburbTypeAdmin(admin.ModelAdmin):
    model = SuburbType
    list_display = [
        "name", "abrev", "icon", "emoji"]
admin.site.register(SuburbType, SuburbTypeAdmin)


class SuburbAdmin(admin.ModelAdmin):
    model = Suburb
    list_display = [
        "cve_col", "name", "short_name", "townhall",
        "sururb_type", "is_pilot"]
    raw_id_fields = ["townhall", "sururb_type", "derivation_suburb"]
admin.site.register(Suburb, SuburbAdmin)
admin.site.register(SuburbGeoData)
