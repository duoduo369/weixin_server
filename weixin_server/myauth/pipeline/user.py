# -*- coding: utf-8 -*-
from myauth.models import UserProfile, UserInvite
from django.contrib.auth.models import User
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
    if not is_new or not user:
        return
    # 二维码扫描
    qrcode = kwargs.get('qrcode')
    if qrcode and qrcode.userprofile_set.all().exists():
        inviter = qrcode.userprofile_set.all()[0].user
        try:
            UserInvite.invite_user(inviter.id, user, only_allow_invited_by_one_user=True)
        except:
            return
        user._inviter = inviter
        return {'inviter': inviter}
    # 点击邀请链接
    next_url = backend.strategy.session_get('next')
    if next_url:
        params = parse_url(next_url)['params']
        inviter_id = params.get('inviter_id')
        if inviter_id and user:
            try:
                inviter = User.objects.get(id=inviter_id)
                UserInvite.invite_user(inviter_id, user, only_allow_invited_by_one_user=True)
            except:
                return
            user._inviter = inviter
        return {'inviter': inviter}
