# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0005_auto_20150818_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerresult',
            name='payload_bytes',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='playerresult',
            name='received_packets',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='playerresult',
            name='transmit_packets',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
