# -*- coding: utf-8 -*-
'''
根据下面的文档提供各种不同的配置

其他的地方建议使用as config的方式，方便改配置
from weixin.config import safe_conf as config

from wechat_sdk import WechatConf
conf = WechatConf(
    token='your_token', 
    appid='your_appid', 
    appsecret='your_appsecret', 
    encrypt_mode='safe',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
    encoding_aes_key='your_encoding_aes_key'  # 如果传入此值则必须保证同时传入 token, appid
)

https://github.com/wechat-python-sdk/wechat-python-sdk/blob/master/wechat_sdk%2Fcore%2Fconf.py

'''

from django.conf import settings
from wechat_sdk import WechatConf

def get_config(encrypt_mode='normal'):
    return WechatConf(
        appid = settings.WEIXIN_APP_ID,
        appsecret = settings.WEIXIN_APP_SECRET,
        token = settings.WEIXIN_TOKEN,
        encrypt_mode=encrypt_mode,
        encoding_aes_key=settings.WEIXIN_ENCODING_AES_KEY,
    )
# 普通模式
normal_conf = get_config(encrypt_mode='normal')
# 兼容模式
compatible_conf = get_config(encrypt_mode='compatible')
# 安全模式
safe_conf = get_config(encrypt_mode='safe')
