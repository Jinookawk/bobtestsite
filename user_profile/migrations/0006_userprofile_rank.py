# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-13 13:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0005_remove_userprofile_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='rank',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
