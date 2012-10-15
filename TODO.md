Stuff to look into
------------------

## Middleware weirdnesses

There is weirdness concerning the middleware. Do we need to set 
django_cas views for login and logout when the middleware intercepts
these view functions? 

Look into django admin authentication/authorization bits in the
middleware and check if they really belong there. Or does django
admin verify it's own authorization?
