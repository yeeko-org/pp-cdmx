# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-15 01:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public_account', '0011_auto_20210614_1859'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='row',
            name='range',
        ),
        migrations.RemoveField(
            model_name='row',
            name='variation_calc',
        ),
    ]
