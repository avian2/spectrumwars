# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import front.models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0014_player_in_use'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='code',
            field=models.TextField(validators=[front.models.check_syntax]),
        ),
        migrations.AlterField(
            model_name='player',
            name='name',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
