# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-15 03:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notice', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('num', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=50)),
                ('created_date', models.DateField(blank=True)),
                ('hits', models.IntegerField(blank=True)),
                ('content', models.TextField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='DjangoBoard',
        ),
    ]
