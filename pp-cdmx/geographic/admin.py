# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import (
    TownHall, TownHallGeoData, SuburbType, Suburb, SuburbGeoData)

admin.site.register(TownHall)
admin.site.register(TownHallGeoData)
admin.site.register(SuburbType)
admin.site.register(Suburb)
admin.site.register(SuburbGeoData)
