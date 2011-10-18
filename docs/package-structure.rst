Package structure
=================

There are ~10 top level packages in ptah.  Each package exports its public
api inside of the __init__.py of the package.  For instance, ptah/cms/__init__.py
contains all of the public API.  Anything *not* defined in the public API is 
considered an implementation detail and will not be documented.

top level package
-----------------

ptah/__init__.py contains  public API that is used nearly everywhere.
these APIs include security, uri, principal events, & token system.  
canonical WSGI factory, make_wsgi_app. 

ptah.addon
----------

This contains a prototype addon subsystem.  Not useful at this time unless
you are a framework developer and interested in helping us build this.

ptah.addon is optional.

ptah.cms
--------

This contains the core CMS functionality such as Node, Content, Type, events, 
ApplicationRoot.  Facilities such as REST action registration also are public
API for this package.

ptah.cms is required.

ptah.cmsapp
-----------

This is a default application of the ptah.cms library.

ptah.cmsapp is optional.

ptah.config
-----------

configuration directives and settings.  helper package which provides
declarative style configuration of ptah functionality.  

ptah.config is required.

ptah.crowd
----------

the default user management facilities. supports User and User Properties
models. login, logout, resetpassword, registration, validation and suspend.

ptah.crowd is optional.

ptah.form
---------

form library which contains fields and form generation.

ptah.form is required.

ptah.manage
-----------

is located at /ptah-manage by default also known as Ptah Manage.  this
provide introspection facilities for your pyramid application.  also gives
nice interface into SQLAlchemy models.

ptah.manage is optional.

view
----

contains the view, library facilitiy, snippet, layout, static resource 
registration, flash messages, formatters.  

ptah.view is required.