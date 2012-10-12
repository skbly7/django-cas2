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

### Configuration options for django-cas2

#### Mandatory setting

`CAS_SERVER_URL: None`,
	Mandatory. The URL for the CAS server.

#### Optional settings

`CAS_EXTRA_LOGIN_PARAMS: None`
	A dictionary of extra URL parameters to add to the login URL when redirecting the user.
	Ex: CAS_EXTRA_LOGIN_PARAMS = {'renew' : 'true'}

`CAS_LOGOUT_COMPLETELY: True`
	If `True`, redirect and do a CAS logout when user logs out of the Django application.

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
	
`CAS_LOGOUT_REQUEST_ALLOWED: ()`
	TODO: DROP THIS AND ONLY ALLOW SERVER IN CAS_SERVER_URL TO LOGOUT, OR REMOVE COMPLETELY.

`CAS_AUTO_CREATE_USERS : False`
	If `True`, automatically create accounts for authenticated users which don't have one. This
	is a change in behavior from the original django-cas module which hade no such option and
	auto created users.

`CAS_ALLOWED_PROXIES : []`
	A list of URLs of proxies that are allowed to proxy authenticate to the Django application.
	If set, the proxy chain provided by the CAS server in the validation response must not contain
	services that are not included in this list. There is currently no wild carding or other magic.


## Rationale for forking

