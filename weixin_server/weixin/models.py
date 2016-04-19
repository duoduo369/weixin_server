# -*- coding: utf-8 -*-
import json
import logging

from uuid import uuid4
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from wechat_sdk.exceptions import OfficialAPIError
from config_models.models import ConfigurationModel
from weixin.wechat import get_wechat
from weixin.qrcode import create_temp_qrcode, create_permanent_qrcode

wechat = get_wechat()

class Menu(ConfigurationModel):
    cache_timeout = 10
    data = models.TextField(default='{}')
    response = models.TextField()

    def save(self, action_type='noaction', *args, **kwargs):
        '''
            action_type: create | delete 只有这两个值时才会与微信服务器交互
        '''
        # TODO: 完善save的这些异常
        response = {}
        weixin_request_type = ''
        try:
            # 如果是取消当前配置的的启用则删除菜单
            if self.enabled and action_type == 'create':
                # 如果是更新则新建
                weixin_request_type = 'create_menu'
                menu_data = json.loads(self.data)
                response = wechat.create_menu(menu_data)
            elif action_type == 'delete':
                weixin_request_type = 'delete_menu'
                response = wechat.delete_menu()
        except OfficialAPIError as ex:
            response = {
                'errcode': ex.errcode,
                'errmsg': ex.errmsg,
            }
            # 如果weixin api调用失败，则此条记录不能激活
            self.enabled = False
        response['action_type'] = action_type
        response['weixin_request_type'] = weixin_request_type
        self.response = json.dumps(response)
        return super(Menu, self).save(*args, **kwargs)


class QRCode(models.Model):

    TEMP_QRCODE_UPDATE_DAYS = 7

    QR_SCENE = 'QR_SCENE'
    QR_LIMIT_SCENE = 'QR_LIMIT_SCENE'
    QR_LIMIT_STR_SCENE = 'QR_LIMIT_STR_SCENE'
    ACTION_NAME_CHOICES = (
        (QR_SCENE, QR_SCENE),
        (QR_LIMIT_SCENE, QR_LIMIT_SCENE),
        (QR_LIMIT_STR_SCENE, QR_LIMIT_STR_SCENE),
    )
    url = models.URLField(blank=True, max_length=255, default='')
    scene_id = models.CharField(blank=True, max_length=255, db_index=True, default='')
    update_time = models.DateTimeField(blank=True, null=True)
    action_name = models.CharField(max_length=30,
            choices=ACTION_NAME_CHOICES, default=QR_SCENE, db_index=True)

    @classmethod
    def get_qrcode(cls, action_name, scene_id):
        now = timezone.now()
        qrcode = None
        try:
            qrcode = cls.objects.get(action_name=action_name, scene_id=scene_id)
            # 临时二维码判断是否过期
            if qrcode.action_name == cls.QR_SCENE:
                if qrcode.update_time and qrcode.url:
                    _delta = now - qrcode.update_time
                    if _delta.days < qrcode.TEMP_QRCODE_UPDATE_DAYS:
                        return qrcode
            else:
                return qrcode
        except cls.DoesNotExist:
            pass
        if not qrcode:
            qrcode = cls(action_name=action_name, scene_id=scene_id)
        qrcode.update_time = now
        if action_name == cls.QR_SCENE:
            qrcode.url = create_temp_qrcode(scene_id)
        else:
            qrcode.url = create_permanent_qrcode(scene_id)
        qrcode.save()
        return qrcode

    @classmethod
    def generate_temp_scene_id(cls, obj_id):
        return int('{}{}'.format(obj_id, uuid4().int)[:20])

    @property
    def qrcode_url(self):
        if not self.action_name or not self.scene_id:
            raise Exception(u'qrcode object must have action_name and scene_id value')
        now = timezone.now()
        # 永久化的二维码不必更新
        if self.action_name != self.QR_SCENE:
            if not self.url:
                self.update_time = now
                self.url = create_permanent_qrcode(self.scene_id)
                self.save()
            return self.url
        # 临时二维码判断是否过期
        if self.update_time and self.url:
            _delta = now - self.update_time
            if _delta.days < self.TEMP_QRCODE_UPDATE_DAYS:
                return self.url
        self.update_time = now
        self.url = create_temp_qrcode(self.scene_id)
        self.save()
        return self.url
