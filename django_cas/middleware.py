""" Django CAS 2.0 authentication middleware """

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, logout as do_logout
from django.contrib.auth.views import login, logout
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django_cas.exceptions import CasTicketException
from django_cas.views import login as cas_login, logout as cas_logout
from urllib import urlencode

__all__ = ['CASMiddleware']

def cas_request_logout_allowed(request):
    """ Checks if the remote server is allowed to send cas logout request.
        If nothing is set in the CAS_LOGOUT_REQUEST_ALLOWED parameter, all remote
        servers are allowed. Be careful!
        
        This does not really work that well for a number of scenarios, including
        when the service is proxied into another web space, in which case 
        X-FORWARDED-FOR may be present instead, or not. Trusting DNS reverse lookup 
        in order to implement 'security' is not really recommended practise.
        
        The security threat handled here is that someone could intercept service
        tickets somehow and use these to logout users. Taken to the extreme,
        this could make out a DOS attack of sorts. The service tickets are short-lived
        for authentication purposes, but long-lived used for single sign out.
        
        But there are a number of other threats that could be used this way, including
        the django session itself which is much more exposed than the service ticket.
    """
    if not settings.CAS_LOGOUT_REQUEST_ALLOWED: 
        return True

    if not request.META.get('REMOTE_ADDR'):
        return False

    try:
        from socket import gethostbyaddr
        remote_host = gethostbyaddr(request.META.get('REMOTE_ADDR'))[0]
    except:
        return False
    allowed_hosts = settings.CAS_LOGOUT_REQUEST_ALLOWED
    return remote_host in allowed_hosts


class CASMiddleware(object):
    """Middleware that allows CAS authentication on admin pages"""

    def process_request(self, request):
        """ Checks that the authentication middleware is installed. """

        error = ("The Django CAS middleware requires authentication "
                 "middleware to be installed. Edit your MIDDLEWARE_CLASSES "
                 "setting to insert 'django.contrib.auth.middleware."
                 "AuthenticationMiddleware'.")
        assert hasattr(request, 'user'), error


    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Forwards unauthenticated requests to the admin page to the CAS
            login URL, as well as calls to django.contrib.auth.views.login and
            logout.
        """
        if view_func in (login, cas_login) and request.POST.get('logoutRequest'):
            if cas_request_logout_allowed(request):
                return cas_logout(request, *view_args, **view_kwargs)
            return HttpResponseForbidden()

        if view_func == login:
            return cas_login(request, *view_args, **view_kwargs)
        if view_func == logout:
            return cas_logout(request, *view_args, **view_kwargs)

        # TODO: should this really be the concern of a CAS middleware?
        # /fjo 2012-10-13
        if not view_func.__module__.startswith('django.contrib.admin.'):
            return None

        if request.user.is_authenticated():
            if request.user.is_staff:
                return None
            else:
                error = ('<html><body><h1>Forbidden</h1><p>You do not have staff privileges.</p></body></html>')
                return HttpResponseForbidden(error)
        params = urlencode({REDIRECT_FIELD_NAME: request.get_full_path()})        
        return HttpResponseRedirect(settings.LOGIN_URL + '?' + params)


    def process_exception(self, request, exception):
        """ When we get a CasTicketException it is probably caused by the ticket timing out.
            So logout and get the same page again."""
        if isinstance(exception, CasTicketException):
            do_logout(request)
            return HttpResponseRedirect(request.path)
        else:
            return None
