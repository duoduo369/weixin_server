# -*- coding: utf-8 -*-
'''微信二维码'''
from .utils import wechat
from django.conf import settings

def create_temp_qrcode_ticket(scene_id, expire_seconds=604800):
    data = {
        "expire_seconds": expire_seconds,
        "action_name": "QR_SCENE",
        "action_info": {
            "scene": {
                "scene_id": scene_id
            }
        }
    }
    response = wechat.create_qrcode(data)
    return response['ticket']


def create_permanent_qrcode_ticket(scene_str):
    data = {
        "action_name": "QR_LIMIT_STR_SCENE",
        "action_info": {
            "scene": {
                "scene_str": scene_str
            }
        }
    }
    response = wechat.create_qrcode(data)
    return response['ticket']


def create_temp_qrcode(scene_id, expire_seconds=604800):
    '''生成临时二维码，有过期时间，无上限'''
    ticket = create_temp_qrcode_ticket(scene_id, expire_seconds)
    response = wechat.show_qrcode(ticket)
    return response.url


def create_permanent_qrcode(scene_str):
    '''生成永久二维码，注意上限10万张，认真思考业务逻辑'''
    ticket = create_permanent_qrcode_ticket(scene_str)
    response = wechat.show_qrcode(ticket)
    return response.url
