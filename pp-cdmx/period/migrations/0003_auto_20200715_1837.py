# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-07-15 23:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('period', '0002_auto_20200714_1248'),
    ]

    operations = [
        migrations.RenameField(
            model_name='periodpp',
            old_name='pdf_iedf',
            new_name='pdf_iecm',
        )
    ]