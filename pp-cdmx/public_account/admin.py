# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import PublicAccount, PPImage

class PPImageInline(admin.StackedInline):
      model = PPImage
      extra = 0


class PublicAccountAdmin(admin.ModelAdmin):
    model = PublicAccount
    list_display = [
        "townhall", "period_pp"]
    inlines=[PPImageInline]
admin.site.register(PublicAccount, PublicAccountAdmin)
