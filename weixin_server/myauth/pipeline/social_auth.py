# -*- coding: utf-8 -*-

def social_user(backend, uid, user=None, *args, **kwargs):
    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    socials = backend.strategy.storage.user.get_social_auth_for_user(user, provider)
    if user and socials.exists():
        _social = socials[0]
        if _social.uid != uid:
            msg = 'Your already bind a {0} account, can not bind again, logout first.'.format(provider)
            raise AuthAlreadyAssociated(backend, msg)
    if social:
        if user and social.user != user:
            msg = 'This {0} account is already in use.'.format(provider)
            raise AuthAlreadyAssociated(backend, msg)
        elif not user:
            user = social.user
    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': False}
