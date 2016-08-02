# -*- coding: utf-8 -*-
import json
import logging

from random import randint
from uuid import uuid4
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from wechat_sdk.exceptions import OfficialAPIError
from config_models.models import ConfigurationModel
from weixin.wechat import get_wechat
from weixin.qrcode import create_temp_qrcode, create_permanent_qrcode
from weixin.utils import create_mch_billno, xml_response_to_dict
from weixin.pay import sendredpack

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
    # QR_SCENE时上限为2**32
    scene_id = models.CharField(blank=True, max_length=255, db_index=True, default='')
    update_time = models.DateTimeField(blank=True, null=True)
    action_name = models.CharField(max_length=30,
            choices=ACTION_NAME_CHOICES, default=QR_SCENE, db_index=True)
    action_type = models.CharField(max_length=255, default='', db_index=True)

    @classmethod
    def get_qrcode(cls, action_name, scene_id, action_type=None):
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
            qrcode = cls(
                    action_name=action_name,
                    scene_id=scene_id,
                    action_type=action_type)
        qrcode.update_time = now
        if action_name == cls.QR_SCENE:
            qrcode.url = create_temp_qrcode(scene_id)
        else:
            qrcode.url = create_permanent_qrcode(scene_id)
        qrcode.save()
        return qrcode

    @classmethod
    def generate_temp_scene_id(cls, obj_id):
        '''max id: 2 ** 32 = 4294967296'''
        return int('{}{}{}'.format(randint(1, 3), obj_id, uuid4().int)[:9])

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


class RedPackTemplate(TimeStampedModel):
    '''
    红包模板，admin配置用
    '''
    GROUPREDPACK = 'groupredpack'
    REDPACK = 'redpack'
    type_choices = (
        (GROUPREDPACK, 'groupredpack'),
        (REDPACK, 'redpack'),
    )
    # 活动, 基本用来后期查一个活动发了多少红包的数据需求
    event = models.CharField(max_length=60, unique=True, db_index=True)
    send_name = models.CharField(max_length=60)
    wishing = models.CharField(max_length=255)
    act_name = models.CharField(max_length=60)
    remark = models.CharField(max_length=255)


class RedPackRecord(TimeStampedModel):
    '''
    请求微信红包接口的记录表
    https://pay.weixin.qq.com/wiki/doc/api/tools/cash_coupon.php?chapter=13_5
    '''
    GROUPREDPACK = 'groupredpack'
    REDPACK = 'redpack'
    type_choices = (
        (GROUPREDPACK, 'groupredpack'),
        (REDPACK, 'redpack'),
    )
    user = models.ForeignKey(User)
    type = models.CharField(choices=type_choices, max_length=60)
    # 活动, 基本用来后期查一个活动发了多少红包的数据需求
    event = models.CharField(max_length=60, db_index=True, default='')
    # 反查id，可以根据这个值反查活动，需要自己定义具体活动id
    reverse_key = models.CharField(max_length=255, db_index=True, default='')
    mch_billno = models.CharField(max_length=60, db_index=True, unique=True)
    mch_id = models.CharField(max_length=60)
    wxappid = models.CharField(max_length=60)
    send_name = models.CharField(max_length=60)
    re_openid = models.CharField(max_length=60, db_index=True)
    total_amount = models.CharField(max_length=60)
    total_num = models.CharField(max_length=60)
    wishing = models.CharField(max_length=255)
    client_ip = models.CharField(max_length=60, default='127.0.0.1')
    act_name = models.CharField(max_length=60)
    remark = models.CharField(max_length=255)
    amt_type = models.CharField(max_length=255, default='')
    status = models.CharField(max_length=255, default='', db_index=True)
    response = models.TextField(default='')
    send_time = models.CharField(max_length=255, default='')
    send_listid = models.CharField(max_length=255, default='')

    @classmethod
    def create_record_from_template(cls, user, re_openid,
            total_amount, total_num, redpack_template,
            type='redpack', reverse_key='', amt_type='',
            client_ip='127.0.0.1'):
        attrs = ['event', 'send_name', 'wishing',  'act_name', 'remark']
        record = cls(
            user=user,
            re_openid=re_openid,
            total_amount=total_amount,
            total_num=total_num,
            type=type,
            reverse_key=reverse_key,
            amt_type=amt_type,
            client_ip=client_ip,
        )
        for attr in attrs:
            setattr(record, attr, getattr(redpack_template, attr))
        record.mch_id = settings.WEINXIN_PAY_MCH_ID
        record.wxappid = settings.WEIXIN_APP_ID
        record.mch_billno = create_mch_billno(settings.WEINXIN_PAY_MCH_ID)
        record.save()
        return record

    @classmethod
    def new_record(cls, user, re_openid, send_name,
            total_amount, total_num, wishing, act_name, remark,
            type='redpack', event='', reverse_key='',
            client_ip='127.0.0.1', amt_type=''):
        record = cls(
            user=user,
            send_name=send_name,
            re_openid=re_openid,
            total_amount=total_amount,
            total_num=total_num,
            wishing=wishing,
            act_name=act_name,
            remark=remark,
            type=type,
            event=event,
            reverse_key=reverse_key,
            client_ip=client_ip,
            amt_type=amt_type
        )
        record.mch_id = settings.WEINXIN_PAY_MCH_ID
        record.wxappid = settings.WEIXIN_APP_ID
        record.mch_billno = create_mch_billno(settings.WEINXIN_PAY_MCH_ID)
        record.save()
        return record

    def send_redpack(self):
        '''如果红包发送成功，不重复调用接口'''
        send = False
        if self.status == 'SUCCESS':
            return (None, send)
        response = sendredpack(
            re_openid=self.re_openid,
            total_amount=self.total_amount,
            total_num=self.total_num,
            send_name=self.send_name,
            mch_billno=self.mch_billno,
            wishing=self.wishing,
            act_name=self.act_name,
            remark=self.remark,
            client_ip=self.client_ip
        )
        self.response = response.content
        if response.status_code < 200 or response.status_code > 299:
            self.status = 'FAIL'
        else:
            rdict = xml_response_to_dict(response)
            if rdict['return_code'] == 'SUCCESS' \
                    and rdict['result_code'] == 'SUCCESS':
                self.status = 'SUCCESS'
                attrs = ['send_time', 'send_listid']
                for attr in attrs:
                    if attr in rdict:
                        setattr(self, attr, rdict[attr])
            else:
                self.status = 'FAIL'
        self.save()
        send = True
        return (response, send)
