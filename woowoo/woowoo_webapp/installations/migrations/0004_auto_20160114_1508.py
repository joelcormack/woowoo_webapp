# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-14 15:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installations', '0003_auto_20160107_1925'),
    ]

    operations = [
        migrations.RenameField(
            model_name='installation',
            old_name='retailer_confirmed',
            new_name='supplier_confirmed',
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(choices=[('K1', 'KL1'), ('K2', 'KL2 prm'), ('K3', 'KL3'), ('Ku', 'KLu'), ('ST', 'STK')], max_length=2, null=True),
        ),
    ]