# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-09 18:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0004_auto_20161110_0251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='created_date',
            field=models.DateField(null=True),
        ),
    ]
