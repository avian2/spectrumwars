# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0011_player_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 24, 13, 12, 57, 303218, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
