# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0009_round_testbed'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='timeline',
            field=models.FileField(default=None, upload_to=b'timeline'),
            preserve_default=False,
        ),
    ]
