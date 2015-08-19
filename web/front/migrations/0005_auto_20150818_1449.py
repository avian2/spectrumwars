# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0004_auto_20150818_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='duration',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='game',
            name='ran',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 18, 14, 49, 32, 285096), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='player',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 18, 14, 49, 37, 877389), auto_now_add=True),
            preserve_default=False,
        ),
    ]
