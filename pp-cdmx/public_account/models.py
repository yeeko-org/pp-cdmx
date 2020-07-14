# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from geographic.models import TownHall
from period.models import PeriodPP


class PublicAccount(models.Model):
    original_pdf = models.FileField(
        upload_to="public_account", blank=True, null=True)
    townhall = models.ForeignKey(TownHall, blank=True, null=True)
    pages = models.TextField(blank=True, null=True)
    period_pp = models.ForeignKey(PeriodPP)

    def __unicode__(self):
        return self.townhall

    class Meta:
        verbose_name = u"Cuenta Publica"
        verbose_name_plural = u"Cuentas Publicas"
