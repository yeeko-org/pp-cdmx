# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class CategoryIEDF(models.Model):
    name = models.CharField(max_length=80)
    year_start = models.IntegerField()
    year_end = models.IntegerField()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "CategoryIEDF"
        verbose_name_plural = "Categories IEDF"
