# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-01 17:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installations', '0010_auto_20160122_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='installation',
            name='long_and_lat',
            field=models.CharField(max_length=50, null=True),
        ),
    ]