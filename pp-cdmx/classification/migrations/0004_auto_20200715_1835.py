# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-07-15 23:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0003_auto_20200715_1240'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CategoryIEDF',
            new_name='CategoryIECM',
        ),
        migrations.AlterModelOptions(
            name='categoryiecm',
            options={'verbose_name': 'Categoria IECM', 'verbose_name_plural': 'Categorias IECM'},
        ),
    ]
