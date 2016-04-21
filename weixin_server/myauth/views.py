# -*- coding: utf-8 -*-
from django.views.generic import View
from djangomako.shortcuts import render_to_response
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect, HttpResponse
#from .decorators import login_required
from django.contrib.auth.decorators import login_required
from social.apps.django_app.utils import load_strategy
from django.core.urlresolvers import reverse


class OauthNewUserView(View):
    '''未登录创建用户成功'''

    def get(self, request):
        return render_to_response('oauth/new_user.html', {})


class OauthNewAssociationView(View):

    def get(self, request):

        logout(request)
        return render_to_response('oauth/new_association.html', {})


class OauthAuthenticationSuccessView(View):
    '''三方登录成功'''

    def get(self, request):
        next_url = request.GET.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)
        return render_to_response('oauth/authentication_success.html', {})


class PersonalCenterView(View):
    '''个人中心'''

    @method_decorator(login_required)
    def get(self, request):
        context = {'user': request.user}
        return render_to_response('myauth/personal_center.html', context)

class InviteUserView(View):
    '''邀请注册'''

    @method_decorator(login_required)
    def get(self, request):
        return HttpResponseRedirect(reverse('myauth:personal-center'))

class LogoutView(View):

    def get(self, request):
        logout(request)
        return HttpResponse(u'您已退出登录')
