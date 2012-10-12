""" CAS login/logout replacement views """

from django.conf import settings
from django.contrib import auth
from django.http import HttpResponseRedirect, HttpResponseForbidden, \
    HttpResponse, HttpResponseNotFound
from django_cas.models import PgtIOU, SessionServiceTicket
from urllib import urlencode
from urlparse import urljoin
from xml.dom import minidom
import logging

__all__ = ['login', 'logout', 'proxy_callback']

logger = logging.getLogger(__name__)

def _service(request):
    """ Returns service host URL as derived from request """

    return ('http://', 'https://')[request.is_secure()] + request.get_host()


def _service_url(request, redirect_to=None):
    """ Returns application service URL for CAS. """
    
    service = _service(request) + request.path
    if not redirect_to:
        return service
    else:
        return ''.join([service,
                        '?' if not '?' in service else '&',
                        urlencode({auth.REDIRECT_FIELD_NAME: redirect_to})])


def _redirect_url(request):
    """ Redirects to referring page, or CAS_REDIRECT_URL if no referrer. """

    if request.GET.get(auth.REDIRECT_FIELD_NAME):
        return request.GET.get(auth.REDIRECT_FIELD_NAME)
    
    if settings.CAS_IGNORE_REFERER:
        return settings.CAS_REDIRECT_URL

    return request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)


def _login_url(service):
    """ Returns a CAS login URL. """

    params = {'service': service}
    if settings.CAS_EXTRA_LOGIN_PARAMS:
        params.update(settings.CAS_EXTRA_LOGIN_PARAMS)
    return urljoin(settings.CAS_SERVER_URL, 'login') + '?' + urlencode(params)


def _logout_url(request, next_page=None):
    """ Returns a CAS logout URL """

    logout_url = urljoin(settings.CAS_SERVER_URL, 'logout')
    if next_page:
        logout_url += '?' + urlencode({'url': _service(request) + next_page})

    return logout_url


def login(request, next_page=None, required=False):
    """ Forwards to CAS login URL or verifies CAS ticket. """

    if not next_page:
        next_page = _redirect_url(request)
        
    single_sign_out_request = request.POST.get('logoutRequest')
    if settings.CAS_SINGLE_SIGN_OUT and single_sign_out_request:
        request.session = _get_session(single_sign_out_request)
        if not request.session:
            return HttpResponseNotFound('<html><body><h1>No Such Session</h1></body></hmtl>')
        request.user = auth.get_user(request)
        logger.debug("Got single sign out callback from CAS for user %s session %s", 
                     request.user, request.session.session_key)
        auth.logout(request)
        return HttpResponse('<html><body><h1>Single Sign Out - Ok</h1></body></html>')
        
    if request.user.is_authenticated():
        return HttpResponseRedirect(next_page)

    service = _service_url(request, next_page)
    ticket = request.GET.get('ticket')
    if not ticket:
        return HttpResponseRedirect(_login_url(service))
       
    user = auth.authenticate(ticket=ticket, service=service)

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect(next_page)
    
    if settings.CAS_RETRY_LOGIN or required:
        return HttpResponseRedirect(_login_url(service))

    return HttpResponseForbidden("<html><body><h1>Login failed</h1></body></html>")
 

def _get_session(logout_response):
    """ Recovers the session mapped with the CAS service ticket
        received in the SAML CAS response at CAS logout.
    """
    try:
        response = minidom.parseString(logout_response)
        ticket = response.getElementsByTagName('samlp:SessionIndex')[0].firstChild.nodeValue
        sst = SessionServiceTicket.objects.get(pk=ticket)
        return sst.get_session()
    except SessionServiceTicket.DoesNotExist:
        logger.info("No session matching single sign out request: %s", ticket)        
    except Exception as e:
        logger.error("Unable to parse logout response from server: %s", e)
    return None


def logout(request, next_page=None):
    """ Redirects to CAS logout page. """

    auth.logout(request)
    if not next_page:
        next_page = _redirect_url(request)
    if settings.CAS_LOGOUT_COMPLETELY:
        return HttpResponseRedirect(_logout_url(request, next_page))
    else:
        return HttpResponseRedirect(next_page)


def proxy_callback(request):
    """Handles CAS 2.0+ XML-based proxy callback call.

        Stores the proxy granting ticket in the database for 
        future use.
    """
    pgtIou = request.GET.get('pgtIou')
    tgt = request.GET.get('pgtId')

    logger.debug("Got proxy callback from CAS server for pgt %s wiht pgtIou %s", tgt, pgtIou)

    if not (pgtIou and tgt):
        return HttpResponse()

    PgtIOU.objects.create(tgt = tgt, pgtIou = pgtIou)
    return HttpResponse()
