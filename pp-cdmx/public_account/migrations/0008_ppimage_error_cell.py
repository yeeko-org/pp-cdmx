# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-08-22 06:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public_account', '0007_ppimage_rows_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='ppimage',
            name='error_cell',
            field=models.TextField(blank=True, null=True, verbose_name='pila de errores'),
        ),
    ]
