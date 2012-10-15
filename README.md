django-cas2
===========

CAS 2.0 authentication module for Django with support for proxy authentication
and single sign out. This project is a fork and rewrite of the original django-cas
module which is found at https://bitbucket.org/cpcc/django-cas/ as of this writing.
It is a drop-in replacement for most cases, but support for old versions of Python
and Django is removed and in the case you need this (you really shouldn't) you
have to look for the django-cas version mentioned above. 

[CAS](http://www.jasig.org/cas), Central Authentication Server, is an open source, 
single sign on solution for web applications. [Django](http://www.djangoproject.com/)
is a Python web application framework.  

More useful detailed information about CAS is the [protocol specification](http://www.jasig.org/cas/protocol)
and the [CAS Proxy Walkthrough](https://wiki.jasig.org/display/CAS/Proxy+CAS+Walkthrough)

## Installation

Run python setup.py install as per usual or mess with your PYTHONPATH appropriately.

### Django configuration

Add the django_cas CASMiddleware and CASBackends to the Django configuration. Note
that you need the Django AuthenticationMiddleware as well.

```
MIDDLEWARE_CLASSES = (
	...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_cas.middleware.CASMiddleware',
    ...
)

AUTHENTICATION_BACKENDS = (
	...
    'django.contrib.auth.backends.ModelBackend',
    'django_cas.backends.CASBackend',
    ...
)
```

The login and logout URLs must be handled in the urls.py file, and to use proxy authentication
support also the proxy call back URL, see optional settings below.

```
...
(r'^accounts/login/$', 'django_cas.views.login'),
(r'^accounts/logout/$', 'django_cas.views.logout'),
...
```


### Configuration options for django-cas2

#### Mandatory setting

`CAS_SERVER_URL: None`,

Mandatory. The URL for the CAS server.

#### Optional settings

`CAS_EXTRA_LOGIN_PARAMS: None`

> Not quite sure what the purpose for this is, anyone using it? 
> /Fredrik Jönsson Oct 15 2012

A dictionary of extra URL parameters to add to the login URL when redirecting the user.

`CAS_RENEW: False`

If `True`, enables the renew feature of CAS, sending renew parameter on login
and verification of tickets to enforce that the login is made with a fresh
username and password verification in the CAS server.

`CAS_LOGOUT_COMPLETELY: True`

If `True`, redirect and do a CAS logout when user logs out of the Django application.
It is in most cases pointless to turn this off unless CAS_RENEW is set. 

`CAS_SINGLE_SIGN_OUT: True`

If `True`, support single sign out reqeusts form the CAS server and sign out of the
Django application when a user signs out of CAS.

`CAS_REDIRECT_URL: '/'`

Default URL to redirect to after login and logout when there is no referrer or next
page provided by Django.

`CAS_IGNORE_REFERER: False`

If `True`, logging out of the application will always send the user to the URL specified by `CAS_REDIRECT_URL`.

`CAS_RETRY_LOGIN: False`

If `True`, redirect back to CAS server if CAS authentication fails.

`CAS_PROXY_CALLBACK: None`

The callback URL the CAS server should use to inject proxy tickets. Setting this enables
proxy granting ticket support. The URL must also be registered in urls.py and handled
by the django_cas.views.proxy_callback, e.g:
`(r'^accounts/login/casProxyCallback$', 'django_cas.views.proxy_callback')`
See [Proxy CAS Authentication](https://github.com/fjollberg/django-cas2/PROXY_AUTHENTICATION.md)
for more information and trouble shooting hints.
	
`CAS_AUTO_CREATE_USERS : False`

If `True`, automatically create accounts for authenticated users which don't have one. This
is a change in behavior from the original django-cas module which hade no such option and
auto created users.

`CAS_ALLOWED_PROXIES : []`

A list of URLs of proxies that are allowed to proxy authenticate to the Django application.
If set, the proxy chain provided by the CAS server in the validation response must not contain
services that are not included in this list. There is currently no wild carding or other magic.

## Security considerations

### Single sign out

There was in the applied single-sign-out patch, and in the 1.0 release of this project
a setting with which you could list hosts which where allowed to do the single sign out
call to the application, CAS_LOGOUT_REQUEST_ALLOWED. This is removed in 1.1. As it was
implemented it did not work in a number of situations, and my belief is that it suggested
security that it doesn't really provide.

The recommendation instead is that if you have conserns with the possibility of denial
of service attacks caused by faked logout requests with compromised CAS session tickets, 
you should turn single sign out support of completely, using CAS_SINGLE_SIGN_OUT = False. 

The issue at hand is that if someone intercepts your service ticket, it can be used to
logout the user from the application at a later point. In this sense, the CAS service ticket
has a long life, wheras it otherwise has a very short life span for authentication. The 
service ticket is sent as an URL parameter and thus generally more exposed (for example
in access logging) than most other authentication data.

The only likely place the service ticket is more exposed than other relevant data, say
the django session, is in the access log files. The possibly increased risk is thus if
the log files are more easily accessible than other harmful data, such as the database, 
or provides another vector of attack. The possible effect of this risk is that users
could be logged out, causing a kind of denial of service.

The CAS_LOGOUT_REQUEST_ALLOWED amended this effect to some extent by given the remote
address in the request, only allow hosts with the correct address as reported by the 
address resolving routines of the server host. This is in itself fraught with a number
of issues, and does not work well for proxied applications. Some of these deficits could
be worked around by additional code.

## Copyrights

The source has been and is licensed by a MIT [license](https://github.com/fjollberg/django-cas2/LICENCE.md).
In other words, do as you please with it, but don't think you can hold us liable for any damage caused
to or by you if you use it.

## Rationale for forking

The django-cas project has been rather poorly maintained for some time. The most obviuos changes
include moving the repo around. Patches supplied by myself in order to support proxy authentication
and by others for single sign out (http://code.google.com/r/arnaudgrausem-django-cas/) have 
not been integrated but are in fact lost in the repo changes.

Also the django_cas project suffers from dead code, some wierdness and support for really, 
really old versions of CAS, Python and Django, bogging it down.

The module is still called django_cas for the time being, the rationale being that it is
a drop-in replacement and I don't want to handle the migrations issues in the database for now.
