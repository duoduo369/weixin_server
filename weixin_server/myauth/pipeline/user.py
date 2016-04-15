# -*- coding: utf-8 -*-
from myauth.models import UserProfile

USER_FIELDS = ['username', 'email']

def save_profile(backend, user, response, *args, **kwargs):
    '''只有第一次的时候更新'''
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile()
        profile.user = user
        details = kwargs.get('details', {})
        profile.name = details.get('username') or profile.name or ''
        profile.avatar = details.get('profile_image_url', '')
        if backend.name.startswith('weixin'):
            profile.weixin_unionid = response.get('unionid', '')
        profile.save()
    return {'profile': profile}
