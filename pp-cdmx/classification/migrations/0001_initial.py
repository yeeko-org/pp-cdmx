# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-05-24 18:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Anomaly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Nombre')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripci\xf3n')),
                ('rules', models.TextField(blank=True, null=True, verbose_name='Reglas')),
                ('color', models.CharField(blank=True, max_length=30, null=True, verbose_name='Color')),
                ('is_public', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Anomal\xeda',
                'verbose_name_plural': 'Anomal\xedas',
            },
        ),
        migrations.CreateModel(
            name='CategoryIECM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='Nombre')),
                ('icon', models.CharField(blank=True, max_length=80, null=True, verbose_name='\xcdcono')),
                ('color', models.CharField(blank=True, max_length=80, null=True, verbose_name='Color')),
                ('year_start', models.IntegerField(blank=True, null=True, verbose_name='A\xf1o de Inicio')),
                ('year_end', models.IntegerField(blank=True, null=True, verbose_name='A\xf1o de Fin')),
            ],
            options={
                'verbose_name': 'Categoria IECM',
                'verbose_name_plural': 'Categorias IECM',
            },
        ),
    ]
