# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-08-21 05:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public_account', '0006_auto_20200820_2315'),
    ]

    operations = [
        migrations.AddField(
            model_name='ppimage',
            name='rows_count',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
