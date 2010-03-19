from urlparse import urljoin
from urllib import urlencode, urlopen
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Tgt(models.Model):
    username = models.CharField(max_length = 255, unique = True)
    tgt = models.CharField(max_length = 255)

    def get_proxy_ticket_for(self, service):
        """Verifies CAS 2.0+ XML-based authentication ticket.

        Returns username on success and None on failure.
        """

        try:
            from xml.etree import ElementTree
        except ImportError:
            from elementtree import ElementTree

        params = {'pgt': self.tgt, 'targetService': service}

        url = (urljoin(settings.CAS_SERVER_URL, 'proxy') + '?' +
               urlencode(params))

        page = urlopen(url)

        try:
            response = page.read()
            tree = ElementTree.fromstring(response)
            if tree[0].tag.endswith('proxySuccess'):
                return tree[0][0].text
            else:
                return None
        finally:
            page.close()

class PgtIOU(models.Model):
    pgtIou = models.CharField(max_length = 255, unique = True)
    tgt = models.CharField(max_length = 255)
    timestamp = models.DateTimeField(auto_now = True)

def get_tgt_for(user):
    return Tgt.objects.get(username = user.username)
