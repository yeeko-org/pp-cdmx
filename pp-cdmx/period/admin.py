# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import LawPP, PeriodPP


class LawPPAdmin(admin.ModelAdmin):
    model = LawPP
    list_display = [
        "publish_year", "name", "file_law", "summary"]
admin.site.register(LawPP, LawPPAdmin)


class PeriodPPAdmin(admin.ModelAdmin):
    model = PeriodPP
    list_display = [
        "year", "is_public", "law_pp", "pdf_iecm"]
admin.site.register(PeriodPP, PeriodPPAdmin)
