# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django_extensions.db.models import TimeStampedModel

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

    def __unicode__(self):
        return self.name
