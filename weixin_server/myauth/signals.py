# -*- coding: utf-8 -*-
from django.dispatch import Signal

create_profile_signal = Signal(providing_args=['instance', 'created'])


def create_profile(sender, instance, created=False, *args, **kwargs):
    from myauth.models import UserProfile
    user = instance
    try:
        user.profile
    except UserProfile.DoesNotExist:
        # 如果没有profile，创建
        UserProfile.create_default_profile(user)
