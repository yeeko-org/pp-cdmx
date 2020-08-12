# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-08-12 21:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('public_account', '0002_auto_20200714_1248'),
    ]

    operations = [
        migrations.CreateModel(
            name='PPImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255)),
                ('json_variables', models.TextField(blank=True, null=True)),
                ('clean_data', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='publicaccount',
            name='original_pdf',
        ),
        migrations.RemoveField(
            model_name='publicaccount',
            name='pages',
        ),
        migrations.AddField(
            model_name='publicaccount',
            name='variables',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ppimage',
            name='public_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='public_account.PublicAccount'),
        ),
    ]
