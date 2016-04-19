# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weixin', '0002_qrcode'),
        ('myauth', '0002_userinvite'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='inviter_qrcode',
            field=models.ForeignKey(to='weixin.QRCode', null=True),
        ),
    ]
