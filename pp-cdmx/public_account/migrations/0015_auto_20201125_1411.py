# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-11-25 20:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public_account', '0014_auto_20201119_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='ppimage',
            name='first_headers_used',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='ppimage',
            name='headers',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ppimage',
            name='table_data',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publicaccount',
            name='ignore_columns',
            field=models.CharField(blank=True, help_text='columnas a ignorar para la alineacion horizontal (4-8)', max_length=50, null=True),
        ),
    ]
