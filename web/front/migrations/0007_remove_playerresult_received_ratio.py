# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0006_auto_20150818_1454'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playerresult',
            name='received_ratio',
        ),
    ]
