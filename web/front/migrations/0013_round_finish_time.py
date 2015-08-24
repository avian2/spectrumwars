# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0012_round_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='finish_time',
            field=models.DateTimeField(null=True),
        ),
    ]
