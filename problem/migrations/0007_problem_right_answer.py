# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-30 19:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0006_auto_20161001_0254'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='right_answer',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
