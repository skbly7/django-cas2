from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _
from django_cas.exceptions import CasTicketException, CasConfigException
from urllib import urlencode, urlopen
from urlparse import urljoin
from xml.dom import minidom

class Tgt(models.Model):
    username = models.CharField(max_length = 255, unique = True)
    tgt = models.CharField(max_length = 255)

    def get_proxy_ticket_for(self, service):
        """ Verifies CAS 2.0+ XML-based authentication ticket.

            Returns username on success and None on failure.
        """
        if not settings.CAS_PROXY_CALLBACK:
            raise CasConfigException("No proxy callback set in settings")

        params = {'pgt': self.tgt, 'targetService': service}
        page = urlopen(urljoin(settings.CAS_SERVER_URL, 'proxy') + '?' + urlencode(params))

        try:
            response = minidom.parseString(page.read())
            if response.getElementsByTagName('cas:proxySuccess'):
                return response.getElementsByTagName('cas:proxyTicket')[0].firstChild.nodeValue
            raise CasTicketException("Failed to get proxy ticket")
        finally:
            page.close()


class PgtIOU(models.Model):
    """ Proxy granting ticket and IOU """
    pgtIou = models.CharField(max_length = 255, unique = True)
    tgt = models.CharField(max_length = 255)
    timestamp = models.DateTimeField(auto_now = True)


class SessionServiceTicket(models.Model):
    """ Handles a mapping between the CAS Service Ticket and the session key
        as long as user is connected to an application that uses the CASBackend
        for authentication
    """
    service_ticket = models.CharField(_('service ticket'), max_length=255, primary_key=True)
    session_key = models.CharField(_('session key'), max_length=40)


    class Meta:
        db_table = 'django_cas_session_service_ticket'
        verbose_name = _('session service ticket')
        verbose_name_plural = _('session service tickets')


    def get_session(self):
        """ Searches the session in store and returns it """
        session_engine = __import__(name=settings.SESSION_ENGINE, fromlist=['SessionStore'])
        SessionStore = getattr(session_engine, 'SessionStore')
        return SessionStore(session_key=self.session_key)


    def __unicode__(self):
        return self.ticket


def _is_cas_backend(session):
    """ Checks if the auth backend is CASBackend """
    backend = session[BACKEND_SESSION_KEY]
    from django_cas.backends import CASBackend
    return backend == '{0.__module__}.{0.__name__}'.format(CASBackend)


@receiver(user_logged_in)
def map_service_ticket(sender, **kwargs):
    """ Creates the mapping between a session key and a service ticket after user
        logged in """
    request = kwargs['request']
    ticket = request.GET.get('ticket')
    if ticket and _is_cas_backend(request.session):
        session_key = request.session.session_key
        SessionServiceTicket.objects.create(service_ticket=ticket,
                                            session_key=session_key)


@receiver(user_logged_out)
def delete_service_ticket(sender, **kwargs):
    """ Deletes the mapping between session key and service ticket after user
        logged out """
    request = kwargs['request']
    if _is_cas_backend(request.session):
        session_key = request.session.session_key
        SessionServiceTicket.objects.filter(session_key=session_key).delete()


def get_tgt_for(user):
    if not settings.CAS_PROXY_CALLBACK:
        raise CasConfigException("No proxy callback set in settings")

    try:
        return Tgt.objects.get(username = user.username)
    except Tgt.DoesNotExist:
        raise CasTicketException("no ticket found for user " + user.username)


def delete_old_tickets(**kwargs):
    """ Delete tickets if they are over 2 days old 
        kwargs = ['raw', 'signal', 'instance', 'sender', 'created']
    """
    sender = kwargs.get('sender')
    now = datetime.now()
    expire = datetime(now.year, now.month, now.day) - timedelta(days=2)
    sender.objects.filter(timestamp__lt=expire).delete()


post_save.connect(delete_old_tickets, sender=PgtIOU)
