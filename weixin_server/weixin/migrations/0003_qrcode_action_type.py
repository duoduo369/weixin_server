# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weixin', '0002_qrcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='qrcode',
            name='action_type',
            field=models.CharField(default=b'', max_length=255, db_index=True),
        ),
    ]
