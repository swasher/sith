# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-11-03 17:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_auto_20161103_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='component',
            name='invoice',
            field=models.CharField(blank=True, max_length=64, verbose_name='Номер счета'),
        ),
    ]