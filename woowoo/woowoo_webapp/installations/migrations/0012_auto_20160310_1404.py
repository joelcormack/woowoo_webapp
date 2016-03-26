# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-10 14:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installations', '0011_installation_long_and_lat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(max_length=60),
        ),
        migrations.AlterField(
            model_name='contact',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='installation',
            name='name',
            field=models.CharField(max_length=60),
        ),
    ]