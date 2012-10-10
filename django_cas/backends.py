"""CAS authentication backend"""

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django_cas.models import Tgt, PgtIOU
from urllib import urlencode, urlopen
from urlparse import urljoin
from xml.etree import ElementTree
import time

__all__ = ['CASBackend']

def verify(ticket, service):
    """ Verifies CAS 2.0+ XML-based authentication ticket.

        Returns username on success and None on failure.
    """
    if settings.CAS_PROXY_CALLBACK:
        params = {'ticket': ticket, 'service': service, 'pgtUrl': settings.CAS_PROXY_CALLBACK}
    else:
        params = {'ticket': ticket, 'service': service}

    url = (urljoin(settings.CAS_SERVER_URL, 'proxyValidate') + '?' + urlencode(params))
    page = urlopen(url)

    try:
        response = page.read()
        tree = ElementTree.fromstring(response)
        if tree[0].tag.endswith('authenticationSuccess'):
            username = tree[0][0].text
            if len(tree[0]) >= 2 and tree[0][1].tag.endswith('proxyGrantingTicket'):
                pgtIou = None
                retries_left = 3
                while not pgtIou and retries_left:
                    try:
                        pgtIou = PgtIOU.objects.get(pgtIou = tree[0][1].text)
                    except ObjectDoesNotExist:
                        time.sleep(1)
                        retries_left -= 1
                try:
                    tgt = Tgt.objects.get(username = username)
                    tgt.tgt = pgtIou.tgt
                    tgt.save()
                except ObjectDoesNotExist:
                    Tgt.objects.create(username = username, tgt = pgtIou.tgt)

                pgtIou.delete()
            return username
        else:
            return None
    finally:
        page.close()


def verify_proxy_ticket(ticket, service):
    """ Verifies CAS 2.0+ XML-based proxy ticket.
        Returns username on success and None on failure.
    """
    params = {'ticket': ticket, 'service': service}

    url = (urljoin(settings.CAS_SERVER_URL, 'proxyValidate') + '?' + urlencode(params))
    page = urlopen(url)

    try:
        response = page.read()
        tree = ElementTree.fromstring(response)
        if tree[0].tag.endswith('authenticationSuccess'):
            username = tree[0][0].text
            proxies = []
            for element in tree[0][1]:
                proxies.append(element.text)
            return {"username": username, "proxies": proxies}
        else:
            return None
    finally:
        page.close()
    

class CASBackend(object):
    """ CAS authentication backend """
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, ticket, service):
        """Verifies CAS ticket and gets or creates User object"""

        username = verify(ticket, service)
        if not username:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # user will have an "unusable" password
            user = User.objects.create_user(username, '')
            user.save()
        return user

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
