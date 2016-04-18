# -*- coding: utf-8 -*-
import urlparse
from functools import wraps
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.decorators import available_attrs
from django.http import QueryDict
from django.http import HttpResponse
import json
from django.core import cache


try:
    cache = cache.get_cache('general')
except:
    cache = cache.cache

DEFAULT_REDIRECT_MESSAGE = u"页面正在跳转，请稍候..."


def redirect_to_login_json(next, login_url=None,
                      redirect_field_name=REDIRECT_FIELD_NAME, redirect_message=DEFAULT_REDIRECT_MESSAGE):
    """
    Redirects the user to the login page, passing the given 'next' page
    """
    if not login_url:
        login_url = settings.LOGIN_URL

    login_url_parts = list(urlparse.urlparse(login_url))
    if redirect_field_name:
        querystring = QueryDict(login_url_parts[4], mutable=True)
        querystring[redirect_field_name] = next
        login_url_parts[4] = querystring.urlencode(safe='/')

    content_json = {"op":"redirect", "url": urlparse.urlunparse(login_url_parts), "msg": redirect_message}
    return HttpResponse(json.dumps(content_json), content_type="text/json")


def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME,redirect_message=DEFAULT_REDIRECT_MESSAGE):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse.urlparse(login_url or
                                                        settings.LOGIN_URL)[:2]
            current_scheme, current_netloc = urlparse.urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            return redirect_to_login_json(path, login_url, redirect_field_name)

        return _wrapped_view
    return decorator


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None, redirect_message=DEFAULT_REDIRECT_MESSAGE):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
        redirect_message=redirect_message
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


