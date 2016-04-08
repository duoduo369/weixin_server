# -*- coding: utf-8 -*-
from .config import normal_conf, compatible_conf, safe_conf
from wechat_sdk import WechatBasic

normal_wechat = WechatBasic(conf=normal_conf)
compatible_wechat = WechatBasic(conf=compatible_conf)
safe_wechat = WechatBasic(conf=safe_conf)
