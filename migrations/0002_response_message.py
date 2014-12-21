# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archives', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='message',
            field=models.CharField(default='', max_length=500),
            preserve_default=False,
        ),
    ]
