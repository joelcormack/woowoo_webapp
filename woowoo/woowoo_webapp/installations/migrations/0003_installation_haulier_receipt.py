# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-04 16:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installations', '0002_auto_20151221_1240'),
    ]

    operations = [
        migrations.AddField(
            model_name='installation',
            name='haulier_receipt',
            field=models.FileField(null=True, upload_to='haulier_receipts/%Y/%m/%d'),
        ),
    ]