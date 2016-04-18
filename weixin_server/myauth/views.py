# -*- coding: utf-8 -*-
from django.views.generic import View
from djangomako.shortcuts import render_to_response
from django.contrib.auth import logout


class OauthNewUserView(View):
    '''未登录创建用户成功'''

    def get(self, request):
        return render_to_response('oauth/new_user.html', {})


class OauthNewAssociationView(View):

    def get(self, request):
        logout(request)
        return render_to_response('oauth/new_association.html', {})


class OauthAuthenticationSuccessView(View):

    def get(self, request):
        return render_to_response('oauth/authentication_success.html', {})
