# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0013_round_finish_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='in_use',
            field=models.BooleanField(default=True),
        ),
    ]
