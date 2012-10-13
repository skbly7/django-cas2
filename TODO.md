Stuff to look into
------------------

## Middleware weirdnesses

There is weirdness concerning the middleware. I moved the single
sign out code to the login method to make it work, but I now
realize that it seems to be run by the middleware, though in that
case the code was possibly blocked by the remote host code. It
was still strange that the logout code was put into the cas logout
view which is a different case altogether. 

Look into django admin authentication/authorization bits in the
middleware and check if they really belong there.   