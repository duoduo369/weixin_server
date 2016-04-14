# -*- coding: utf-8 -*-
from django.conf import settings
from .config import get_config
from wechat_sdk import WechatBasic

def get_wechat(encrypt_mode=settings.WEIXIN_ENCRYPT_MODE):
    '''实时生成wechat'''
    conf = get_config(encrypt_mode=encrypt_mode)
    wechat = WechatBasic(conf=conf)
    return wechat
