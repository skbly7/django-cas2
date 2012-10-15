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

## Development proxy authentication with runserver

Setting up proxy authentication in a development environment is a bit complicated since
you need both a proper certificate, ssl support, and a server that allows for at least
two simultaneous requests. It must also be possible for the CAS server to connect
to your host using the host name in your certificate so you need some form of addressing
of your development host which your server can resolve.

### Django concurrent test server

Download django_concurrent_test_server, currently hosted at 
http://github.com/jaylett/django_concurrent_test_server

Just copy the directory somewhere on your PYTHONPATH and include django_concurrent_test_server
in INSTALLED_APPS in your Django settings (settings.py) Or, You can install the application with pip:
```
pip install -e git+git://github.com/jaylett/django_concurrent_test_server.git#egg=django_concurrent_test_server
```

The server works pretty much as the normal test server and you start the server with the 0.0.0.0
address to allow connections on any IP address and not just the local host (127.0.0.1) which is
default.
```
python manage.py runconcurrentserver 0.0.0.0:8000
```

### stunnel, see http://www.stunnel.org/

For SSL support you can use stunnel with the test server.
It reuqires the following configuration file given as argument. Web
browers are more forgiving, but the CAS login server really needs to be
able to verify the certificate. Hence the certificate must be a proper
certificate and include the entire path to the authorizing certificate,
see section about Creating a valid certificate below.
sslVersion=all is significant, since CAS proxy validation fails
for any other value for some reason.

Install stunnel and create a configuration file for it. Make sure you are
running stunnel4 since stunnel3 does not support passing a configuration file.
```
pid=
foreground=yes

[https]
accept=443
connect=8000
cert = /path/to/certs/chain-xxx.org.pem
key = /path/to/certs/xxx.org.key
sslVersion=all
```

Then start stunnel as root if you want to serve on the 443 port. You could
choose a higher port number and configure your system accordingly instead.
```
sudo stunnel stunnel.conf
```

Test your connection by trying to connect to the SSL server on your host, 
https://yourhost/. Make sure you see the two calls to casProxyCallback in
the log file along the lines of:
```
[07/Mar/2011 16:34:40] "GET /accounts/login/ HTTP/1.1" 302 0
[07/Mar/2011 16:34:43] "GET /accounts/login/casProxyCallback HTTP/1.1" 200 0
[07/Mar/2011 16:34:43] "GET /accounts/login/casProxyCallback?pgtIou=PGTIOU-1307-0nYq4SJ6PIfCLHPMrAohyi6h6d93UTbhWqC&pgtId=TGT-4844-9erlFkrLf6RApy13JbFLQkpbg7gXYNa6fhM-50 HTTP/1.1" 200 0
[07/Mar/2011 16:34:44] "GET /accounts/login/?next=%2F&ticket=ST-5235-nauq4pPh4PSBUcCTCBPJeZKoWcJLMemIvmi-20 HTTP/1.1" 302 0
[07/Mar/2011 16:34:44] "GET / HTTP/1.1" 200 14077
```

## CAS servers which requires callback at root

> This was added to the original README by someone. I don't know if it's valid for
> anyone. If it is, your server is broken and does not follow the CAS protocol
> specification, but I keep it here for now.
>
> /Fredrik Jönsson Oct 12 2012.

The callback url for some SSO server implementations may need to be at the root
in this case you will need to add the following to your sites home page view 
in django rather than handle proxy validation via a separate entry in URLs, or 
handle it in some middleware. 

```
if request.GET.get('pgtIou',''):
    from django_cas.views import proxy_callback
    return proxy_callback(request)
```