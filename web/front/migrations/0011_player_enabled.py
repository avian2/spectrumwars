# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0010_game_timeline'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='enabled',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
