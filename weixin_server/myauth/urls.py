# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from .views import (OauthNewUserView, OauthNewAssociationView,
    OauthAuthenticationSuccessView, PersonalCenterView, InviteUserView,
    LogoutView)

urlpatterns = [
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^invite/$', InviteUserView.as_view(), name='invite-user'),
    # 新用户
    url(r'^oauth/newusers/$', OauthNewUserView.as_view(), name='oauth-newuser'),
    # 用户关联新三方
    url(r'^oauth/newassociation/$', OauthNewAssociationView.as_view(), name='oauth-newassociation'),
    # 用户登录成功
    url(r'^oauth/authentication/success/$', OauthAuthenticationSuccessView.as_view(), name='oauth-authentication-success'),
    url(r'^oauth/authentication/success/$', OauthAuthenticationSuccessView.as_view(), name='oauth-authentication-success'),
    url(r'^personal/center/$', PersonalCenterView.as_view(), name='personal-center'),
]
