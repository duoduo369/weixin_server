# -*- coding: utf-8 -*-
import importlib
from django.conf import settings

wechat_module = importlib.import_module('weixin.wechat')
wechat = getattr(wechat_module, '{}_wechat'.format(settings.WEIXIN_ENCRYPT_MODE))
