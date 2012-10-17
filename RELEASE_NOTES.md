Release Notes
-------------

* Dropped django_cas.decorators. This refactorization enters Django 1.4 land.
  The funcionality of django_cas.decorators is available in the standard
  permission_required decorator in Django 1.4, using the option raise_exception.
  
  E.g:
  ```
  from django.contrib.auth.decorators import permission_required
  
  @permission_required(raise_exception=True)
  def view_function():
      ...
  ```
  If you need this decorator, upgrade to Django 1.4 if you haven't already.

## Version KTH-1.2.0

* Dropped 'next_page' and 'required' parameters from views.login and
  'next_page' from views.logout. I did not see a proper use case for these
  parameters and will regard these as undocumented private features,
  hence only a minor version number bump.
* Fix possible UnicodeEncodeErrors in GET parameters. The only actual
  case I've seen of actually using the parameters mentioned above.

## Version KTH-1.1.0

* Add CAS_RENEW setting to enforce CAS renew feature. See [README](./README.md)
  regarding this setting and CAS_LOGOUT_COMPLETELY.
* Dropped the CAS_LOGOUT_REQUEST_ALLOWED setting. It implicated in my view 
  security it didn't really provide. See [README](./README.md) for more information.

## Version KTH-1.0
 
* Completed fork of project.

## Version 2.0.3-KTH-11

* Incorporated support for single sign out. 
* Project has since then moved to other repository and all pull requests 
  seem to be thrown away, so the project seems officially a dead end 
  for other purposes than the ones intended by the maintainer.
* Heavily refactorized.
  * Removed support for CAS 1.0.
  * Removed support for old Python versions.
  * Removed lots of other dead code.
  * Improved XML handling.
  * Added logging.
  * Lots of clean ups.
* Add setting CAS_SINGLE_SIGN_OUT True/False to allow for turning 
  off single sign out support, default True.
* Add setting CAS_ALLOWED_PROXIES [list of URLS] to support basic 
  filtering of allowed proxy servers, not tested.
* Add setting CAS_AUTO_CREATE_USERS True/False to control behavior
  where backend auto creates users that are logged in, default False.

## Version 2.0.3-KTH-10
 
* Added support for CAS proxy authentication.
* Removed messaging.
