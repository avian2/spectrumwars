# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0008_auto_20150819_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='testbed',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
