# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-14 07:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0012_auto_20161013_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='solve_user',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='tags',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
