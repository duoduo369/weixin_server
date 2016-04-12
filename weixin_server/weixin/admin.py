# -*- coding: utf-8 -*-
import json
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from weixin.models import Menu
from wechat_sdk.exceptions import OfficialAPIError
from config_models.admin import ConfigurationModelAdmin
from weixin.utils import wechat

class MenuAdmin(ConfigurationModelAdmin):

    readonly_fields = ('response',)

    def get_actions(self, request):
        return {
            'revert': (
                MenuAdmin.revert,
                'revert',
                _('Revert to the selected configuration')),
            'delete_weixin_menu': (
                MenuAdmin.delete_weixin_menu,
                'delete_weixin_menu',
                _('Delete weixin menu'),
            )
        }

    def delete_weixin_menu(self, request, queryset):
        try:
            response = wechat.delete_menu()
        except OfficialAPIError as ex:
            response = json.dumps({"errcode": ex.errcode ,"errmsg":ex.errmsg})
            # 如果weixin api调用失败，则此条记录不能激活
        menu = self.model()
        menu.response = response
        menu.data = '{}'
        menu.enabled = False
        menu.save()

        return HttpResponseRedirect(reverse('admin:{}_{}_changelist'.format(
            self.model._meta.app_label, self.model._meta.model_name,)))


admin.site.register(Menu, MenuAdmin)
