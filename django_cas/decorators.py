""" Replacement authentication decorators that work around redirection loops """

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseForbidden, HttpResponseRedirect
from functools import wraps
from urllib import urlencode

__all__ = ['permission_required', 'user_passes_test']

def user_passes_test(test_func, 
                     login_url=settings.LOGIN_URL,
                     redirect_field_name=REDIRECT_FIELD_NAME):
    """Replacement for django.contrib.auth.decorators.user_passes_test that
    returns 403 Forbidden if the user is already logged in.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            elif request.user.is_authenticated():
                return HttpResponseForbidden('<html><body><h1>Permission denied</h1></body></html>')
            else:
                return HttpResponseRedirect(login_url + '?' + urlencode({redirect_field_name : request.get_full_path()}))
        return wrapper
    return decorator


def permission_required(perm, login_url=None):
    """Replacement for django.contrib.auth.decorators.permission_required that
    returns 403 Forbidden if the user is already logged in.
    """

    return user_passes_test(lambda u: u.has_perm(perm), login_url=login_url)
