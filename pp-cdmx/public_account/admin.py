# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import PublicAccount


class PublicAccountAdmin(admin.ModelAdmin):
    model = PublicAccount
    list_display = [
        "original_pdf", "townhall", "pages", "period_pp"]
admin.site.register(PublicAccount)
