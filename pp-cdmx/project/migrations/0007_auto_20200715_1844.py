# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-07-15 23:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_auto_20200715_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='category_iecm',
            field=models.IntegerField(blank=True, null=True, verbose_name='Categoria IECM'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name_iecm',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Nombre del IECM'),
        ),
    ]
