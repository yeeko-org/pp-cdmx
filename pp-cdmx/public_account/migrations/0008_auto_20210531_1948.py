# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-01 00:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public_account', '0007_auto_20210531_1910'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='row',
            name='category',
        ),
        migrations.RemoveField(
            model_name='rowcategory',
            name='category',
        ),
        migrations.DeleteModel(
            name='CategoryOllin',
        ),
    ]