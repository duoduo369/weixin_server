# -*- coding: utf-8 -*-
import xmltodict
from django.conf import settings
from datetime import datetime
from uuid import uuid4

def xml_response_to_dict(rep):
    d = xmltodict.parse(rep.content)
    return dict(d['xml'])


def create_mch_billno(mch_id):
    now = datetime.now()
    randuuid = uuid4()
    mch_billno = '{}{}{}'.format(mch_id, now.strftime('%Y%m%d'), str(randuuid.int)[:10])
    return mch_billno
