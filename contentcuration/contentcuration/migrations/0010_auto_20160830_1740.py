# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-31 00:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contentcuration', '0009_remove_channel_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentnode',
            name='sort_order',
            field=models.FloatField(default=1, help_text='Ascending, lowest number shown first', max_length=50, verbose_name='sort order'),
        ),
    ]
