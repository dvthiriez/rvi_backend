# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0014_auto_20151002_2316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remote',
            name='rem_uuid',
            field=models.CharField(default=b'b41c5c62-a5f4-412a-9c08-4b74578b41de', verbose_name=b'Remote UUID', unique=True, max_length=60, editable=False),
            preserve_default=True,
        ),
    ]
