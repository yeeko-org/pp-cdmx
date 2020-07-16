# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-07-15 23:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_auto_20200715_1844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='category_iecm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='classification.CategoryIECM', verbose_name='Categoria IECM'),
        ),
    ]
