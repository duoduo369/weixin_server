# -*- coding: utf-8 -*-
from myauth.models import UserProfile, UserInvite
from utils.https import parse_url

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


def invite_user(backend, user, response, *args, **kwargs):
    is_new = kwargs['is_new']
    next_url = backend.strategy.session_get('next')
    params = parse_url(next_url)['params']
    inviter_id = params.get('inviter_id')
    if inviter_id and is_new and user:
        UserInvite.invite_user(inviter_id, user, only_allow_invited_by_one_user=True)
    return {'inviter_id': inviter_id}
