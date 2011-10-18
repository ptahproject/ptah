Code Examples
=============

Let's `paint by numbers` with a few code examples.  The examples are found in the devel repo, the same mentioned in install.rst. These examples are aimed to be used by either environment, virtualenv or buildout.

.. WSGI App in 5 Lines
.. -------------------

.. ptah.make_wsgi_app is the standard WSGI way of configuring an app.  you can see its usage in start.py you will need to pass a path to the .ini settings file.  for instance, python2.7 start.py ./ptah.ini

..   file: start.py

Dispatch and Traversal
----------------------

This assumes that devapp is on your path, as it will bootstrap itself during ptah startup and provide models.  We need some of the models and records to demonstrate the routing and traversal examples.  We also add a content model. 

  .. literalinclude:: 
     examples/basics101.py
  
Authentication Provider and URI
-------------------------------

This example provides a example authentication provider with URI structure.  This user will be able to create content and you will be able to see (using SQLAlchemy in Ptah Manage) the owner of the item being the example user URI.

  .. literalinclude::
     examples/auth_provider.py

.. Doing Everything Yourself
.. -------------------------

.. We remove Ptah App, devapp and are left only with Ptah CMS.  This example is meant to demonstrate low level configuration and if you want to start using the framework with much fewer opinions.  Going to http://localhost:8080/ will throw a NotFound (there is no Ptah App) but you can still reach Ptah Manage, http://localhost:8080/ptah-manage/ so you have access to all introspection services of your application.

..   file: start4.py
