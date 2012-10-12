# CAS proxy authentication

This module supports CAS proxy authentication for machine to machine authentication
on behalf of a user. For more information details, see [Proxy CAS Walkthrough](https://wiki.jasig.org/display/CAS/Proxy+CAS+Walkthrough)

## CAS proxy callback

The CAS server injects a proxy granting ticket using a secure call to the application
at an URL specified by the `CAS_PROXY_CALLBACK` setting. CAS requires that the server
can not only do https but also provide an verifiable certificate, see below.

In addition, the URL specified in CAS_PROXY_CALLBACK must be added to urls.py and 
directed to the django_cas.views.proxy_callback handler.

## SSL certificate issues

You must ensure that the proxying server not only has SSL but that SSL has the full
chain of valid certificates. If the CAS server cannot verify the certificate of the 
client it will simply reject the client and not do proxy auhentication and inject
a proxy granting ticket. Ordinary authentication will still work. You can use
the openssl utility to investigate the certificate your server publishes.

```
openssl s_client -connect your.proxy.server:443 -verify 3 -pause -showcerts 
```

## CAS servers which requires callback at root

```
This was added to the original README by someone. I don't know if it's valid for
anyone. If it is, your server is broken and does not follow the CAS protocol
specification, but I keep it here for now.

/Fredrik Jönsson Oct 12 2012.
``` 

The callback url for some SSO server implementations may need to be at the root
in this case you will need to add the following to your sites home page view 
in django rather than handle proxy validation via a separate entry in URLs, or 
handle it in some middleware. 

```
if request.GET.get('pgtIou',''):
    from django_cas.views import proxy_callback
    return proxy_callback(request)
```