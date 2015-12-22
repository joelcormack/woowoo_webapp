# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-21 12:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='installation',
            name='provisional_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='installation',
            name='address_two',
            field=models.CharField(max_length=50, null=True),
        ),
    ]