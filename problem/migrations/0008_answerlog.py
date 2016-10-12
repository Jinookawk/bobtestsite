# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-08 06:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('problem', '0007_problem_right_answer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answerlog',
            fields=[
                ('num', models.AutoField(primary_key=True, serialize=False)),
                ('submit_answer', models.CharField(max_length=50, null=True)),
                ('submit_date', models.DateTimeField(auto_now_add=True)),
                ('submitter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]