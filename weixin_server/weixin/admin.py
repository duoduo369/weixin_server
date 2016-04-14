# -*- coding: utf-8 -*-
import json
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from weixin.models import Menu
from wechat_sdk.exceptions import OfficialAPIError
from config_models.admin import ConfigurationModelAdmin
from weixin.wechat import get_wechat

wechat = get_wechat()


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

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        obj.save(action_type='create')

    def revert(self, request, queryset):
        """
        Admin action to revert a configuration back to the selected value
        """
        if queryset.count() != 1:
            self.message_user(request, _("Please select a single configuration to revert to."))
            return
        target = queryset[0]
        target.id = None
        target.changed_by = request.user
        target.save(action_type='create')
        self.message_user(request, _("Reverted configuration."))
        return HttpResponseRedirect(
            reverse(
                'admin:{}_{}_change'.format(
                    self.model._meta.app_label,
                    self.model._meta.model_name,
                ),
                args=(target.id,),
            )
        )

    def delete_weixin_menu(self, request, queryset):
        menu = self.model()
        menu.changed_by = request.user
        menu.data = '{}'
        menu.enabled = False
        menu.save(action_type='delete')
        self.message_user(request, _("Delete Weixin Menu."))
        return HttpResponseRedirect(reverse('admin:{}_{}_changelist'.format(
            self.model._meta.app_label, self.model._meta.model_name,)))


admin.site.register(Menu, MenuAdmin)
