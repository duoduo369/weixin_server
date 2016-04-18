# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django_extensions.db.models import TimeStampedModel
from django.core.urlresolvers import reverse

class UserProfile(TimeStampedModel):

    user = models.OneToOneField(User, related_name='profile')
    name = models.CharField(blank=True, max_length=255, db_index=True)
    avatar = models.URLField(blank=True, max_length=255, default='')
    weixin_unionid = models.CharField(
            max_length=255, db_index=True, default='')

    @classmethod
    def create_default_profile(cls, user):
        profile = cls()
        profile.user = user
        profile.name = ''
        profile.avatar = ''
        weixin_unionid = ''
        profile.save()

    class Meta:  # pylint: disable=missing-docstring
        db_table = "auth_userprofile"

    @property
    def invite_url(self):
        return 'http://{}{}?inviter_id={}'.format(
                settings.SITE_NAME, reverse('myauth:invite-user'), self.user.id)

    def __unicode__(self):
        return self.name


class UserInvite(TimeStampedModel):
    """
    一个人只能被邀请一次
    """
    # 被邀请者
    user = models.OneToOneField(User)
    # 邀请者
    inviter = models.ForeignKey(User, related_name='invitees')
    create_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now_add=True)
    STATUS = {
        'banned': -1,
        'activated': 1,
        'enrolled': 2,
        'final': 4
    }
    status = models.SmallIntegerField(default=0)
    comment = models.CharField(max_length=255, blank=True)

    @classmethod
    def invite_user(cls, inviter_id, user, only_allow_invited_by_one_user=True):
        """ Create inviter data for user. """
        try:
            # 如果被人邀请过了则不再有其他的操作
            if only_allow_invited_by_one_user and \
                cls.objects.filter(user=user).exists():
                    return
            inviter = User.objects.get(id=inviter_id)
            user_invite = cls(user=user, inviter=inviter)
            user_invite.save()
            if user.is_active:
                user_invite.set_status(UserInvite.STATUS['activated'])
        except:
            pass
