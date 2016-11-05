# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-05 10:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('num', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=50, null=True)),
                ('created_date', models.DateField(blank=True)),
                ('hits', models.IntegerField(blank=True)),
                ('filelist', models.CharField(max_length=500, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
