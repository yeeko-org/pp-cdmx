# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-01 00:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public_account', '0006_auto_20210531_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rowcategory',
            name='value',
            field=models.SmallIntegerField(default=0),
        ),
    ]
