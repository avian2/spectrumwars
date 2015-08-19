# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0007_remove_playerresult_received_ratio'),
    ]

    operations = [
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('started', models.DateTimeField(auto_now_add=True)),
                ('nplayers', models.IntegerField()),
                ('state', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='round',
            field=models.ForeignKey(default=0, to='front.Round'),
            preserve_default=False,
        ),
    ]
