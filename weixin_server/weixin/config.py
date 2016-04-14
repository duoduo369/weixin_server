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
import requests
import time
from django.conf import settings
from django.core.cache import cache
from wechat_sdk import WechatConf

WEIXIN_ACCESS_TOKEN_CACHE_KEY = 'weixin_access_token'
WEIXIN_ACCESS_TOKEN_EXPIRES_AT_CACHE_KEY = 'weixin_access_token_expires_at'
WEIXIN_ACCESS_CACHE_TIME = 60 * 60


def set_access_token_function(access_token, access_token_expires_at):
    cache.set(WEIXIN_ACCESS_TOKEN_CACHE_KEY, access_token,
            WEIXIN_ACCESS_CACHE_TIME)
    cache.set(WEIXIN_ACCESS_TOKEN_EXPIRES_AT_CACHE_KEY,
            access_token_expires_at, WEIXIN_ACCESS_CACHE_TIME)


def get_access_token_function():
    access_token = cache.get(WEIXIN_ACCESS_TOKEN_CACHE_KEY)
    access_token_expires_at = cache.get(WEIXIN_ACCESS_TOKEN_EXPIRES_AT_CACHE_KEY)
    if not access_token or not access_token_expires_at:
        response = requests.get(
            url="https://api.weixin.qq.com/cgi-bin/token",
            params={
                "grant_type": "client_credential",
                "appid": settings.WEIXIN_APP_ID,
                "secret": settings.WEIXIN_APP_SECRET,
            }
        )
        response_json = response.json()
        access_token = response_json['access_token']
        access_token_expires_at = int(time.time()) + response_json['expires_in']
        set_access_token_function(access_token, access_token_expires_at)
    return access_token, access_token_expires_at


def get_config(encrypt_mode='normal'):
    return WechatConf(
        appid = settings.WEIXIN_APP_ID,
        appsecret = settings.WEIXIN_APP_SECRET,
        token = settings.WEIXIN_TOKEN,
        encrypt_mode=encrypt_mode,
        encoding_aes_key=settings.WEIXIN_ENCODING_AES_KEY,
        access_token_getfunc=get_access_token_function,
        access_token_setfunc=set_access_token_function,
    )
