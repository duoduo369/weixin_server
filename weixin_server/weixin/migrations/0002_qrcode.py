# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weixin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QRCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(default=b'', max_length=255, blank=True)),
                ('scene_id', models.CharField(default=b'', max_length=255, db_index=True, blank=True)),
                ('update_time', models.DateTimeField(null=True, blank=True)),
                ('action_name', models.CharField(default=b'QR_SCENE', max_length=30, db_index=True, choices=[(b'QR_SCENE', b'QR_SCENE'), (b'QR_LIMIT_SCENE', b'QR_LIMIT_SCENE'), (b'QR_LIMIT_STR_SCENE', b'QR_LIMIT_STR_SCENE')])),
            ],
        ),
    ]
