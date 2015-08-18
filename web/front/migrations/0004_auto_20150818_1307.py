# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0003_game_playerresult'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerresult',
            name='crashed',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='playerresult',
            name='log',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='playerresult',
            name='received_ratio',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='playerresult',
            name='timeline',
            field=models.FileField(default=None, upload_to=b'timeline'),
            preserve_default=False,
        ),
    ]
