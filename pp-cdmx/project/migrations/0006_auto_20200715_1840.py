# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-07-15 23:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_auto_20200715_1829'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='category_iedf',
            new_name='category_iecm',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='name_iedf',
            new_name='name_iecm',
        )
    ]