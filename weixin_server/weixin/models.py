# -*- coding: utf-8 -*-
import json
import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from wechat_sdk.exceptions import OfficialAPIError
from config_models.models import ConfigurationModel
from weixin.utils import wechat

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
                print 'delete_menu'
                print response
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
