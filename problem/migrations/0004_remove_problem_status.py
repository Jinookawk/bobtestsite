# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-17 15:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0003_problem_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='status',
        ),
    ]
