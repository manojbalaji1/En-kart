# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-16 14:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myshop', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='password',
            new_name='pas',
        ),
    ]
