# -*- coding: utf-8 -*-
from myauth.models import UserProfile

USER_FIELDS = ['username', 'email']

def save_profile(backend, user, response, *args, **kwargs):
    '''只有第一次的时候更新'''
    need_save = False
    details = kwargs.get('details', {})
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile()
        profile.user = user
        profile.name = details.get('username') or profile.name or ''
        need_save = True
    if not profile.avatar:
        profile.avatar = details.get('profile_image_url', '')
        if profile.avatar:
            need_save = True
    if backend.name.startswith('weixin'):
        unionid = response.get('unionid', '')
        if unionid and not profile.weixin_unionid:
            profile.weixin_unionid = unionid
            need_save = True
    if need_save:
        profile.save()
    return {'profile': profile}
