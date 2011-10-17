Authentication Service
======================

Need to integrate user logins to new authentication service?  Such as
LDAP, OAuth, Openid, Mongo, or ZODB?  It is very easy to do this.

There are 3 required facilities and 1 optional you provide:

  - User provider, required
  - User resolver, required
  - Password changer, required
  - User searcher, optional

Example
-------

You can find an "in-memory" user provider in examples/auth_provider.py

User provider
-------------

A Principal (User) must have at least 3 attributes:

  * user.uri,  which must be resolvable to the User model
  
  * user.login, which is identifier such as username
  
  * user.name, ?

The Provider class provides 2 methods:

  * authenticate, which takes a mapping {'login':'user', 'password':'pw'}

  * get_principal_bylogin, which takes a login string and returns User

You register a Provider by calling `ptah.register_auth_provider` and 
provide a `uri scheme` and instance.

User resolver
-------------

Resolvers in Ptah are the way we indirect lookup between components.  For
instance, instead of storing the primary key of the user for say, the
ptah_cms_node.Owner field; we make that a string and store a URI.  URIs
can be resolved into a object.

This code registeres a function which returns a object given a URI::

    @ptah.register_uri_resolver('user+crowd', 'Crowd principal resolver')
    def getPrincipal(uri):
        return User.get(uri)

Any uri prefixed with 'user+crowd' will be sent to this function, `getPrincipal`.
For instance, uri.resolve('user+crowd:bob') would be sent to getPrincipal to
return a Principal with that uri.

Password changer
----------------

A function which is responsible for changing a user's password.  An example::

    def change_pwd(principal, password):
        principal.password = password

Principal searcher
------------------

A function which accepts a string and returns a iterator.  This is registered
with URI scheme and function::

    import ptah
    ptah.register_principal_searcher('user+crowd', search)

Superuser
---------

There is another authentication service, ptah+auth which provides a sole
superuser Principal.  The name is `superuser`.  It is a special Principal.
You can not login with this Prinipcal.  It is useful for integration tests.

Outstanding questions
---------------------

1. If you do not provide these services should you raise NotImplementedError?
   Should you just return None?

