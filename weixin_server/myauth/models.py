# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django_extensions.db.models import TimeStampedModel
from .signals import create_profile, create_profile_signal

class UserProfile(TimeStampedModel):

    user = models.OneToOneField(User, related_name='profile')
    name = models.CharField(blank=True, max_length=255, db_index=True)
    avatar = models.URLField(blank=True, max_length=255, default='')

    class Meta:  # pylint: disable=missing-docstring
        db_table = "auth_userprofile"

    def __unicode__(self):
        return self.name

post_save.connect(create_profile, sender=User)
create_profile_signal.connect(create_profile, sender=User)
