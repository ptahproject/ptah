================
Manage Interface
================

The Ptah Management UI is a dashboard into your application.  The Manage
Interface is simple, extensible, and has quite a few features out of the box.  

By default the Manage Interface is disabled.

managers sequence are login attributes from the ``ptah.auth_service``::

    >> from ptah import auth_service
    >> print auth_service.get_current_principal().login
    >> runyaga@gmail.com

Configuring
===========

The `Manage Interface` is configured through Ptah Settings.  You will do this inside of your WSGI entry point where you return make_wsgi_app(). `config` is the Pyramid configurator.::

    config.ptah_init_manage(
        managers = ['*'],
        disable_modules = ['rest', 'introspect', 'apps', 'permissions', 'settings'])

Enable
------

Inside of Ptah Settings you can set the `managers` argument the  userid's you want to allow access.  * means everyone.  By default it is empty and no one is allowed access.  Granting everyone::

  managers = ['*']
  
Granting a few people::

  managers = ['bob@dobbs.com', 'runyaga@gmail.com']

Disable
-------

By default the Manage Interface is disabled.  If Manage Interface is enabled but you want to prevent users from able to access it add the following to your .ini file::

  ptah.manage = ""

Out-of-the-box Modules
======================

The listing of modules you see when you open up http://localhost:6543/ptah-manage interface are all modules which your account has permission to view.  Below are the out-of-the-box modules and a description.

REST
----

This module provides a interactive javascript REST introspector for the Ptah application.  If you want to see this in action see the `ptah_minicms` in examples repository.

Introspect
----------

A comprehensive view into all registrations in your application.  It provides mechanisms to query URI's, see events registered, subscribers, and you can jump directly to the source code where registration takes place.

Permissions
-----------

A list of permission sets which are used by all applications running in the system.  

Settings
--------

Listing of all settings for Pyramid and Ptah.  Ptah has extra settings features.  This settings module will show more variables than the .ini file that you used to start Pyramid.  These extra settings are from Ptah such as :py:class:`ptah.formatter` strings.

SQLAlchemy
----------

Uses SQLAlchemy reflection capabilities to display all tables & rows that are accessible in the database.  If a table is polymorphic it is not editable.   

Models
------

CRUD (CReate Update and Delete) interface for models.  Displays a list of registered models, allows you to modify the records.  

Applications
------------

A list of all Ptah applications registered in the system.  

Field types
-----------
A preview of most registered form Fields in the system.  If a field does not provide a preview it will now show up.  You can see how each field will be rendered.

Extending
=========

The simplest module example to look at is in `ptah/manage/rest.py` which registers a template.  

Module
------

Create a class which subclasses `ptah.manage.PtahModule`.  Decorate the class with :py:func:`ptah.manage.module` decorate.  The label you register using the manage.module decorator is the internal key for that module.  If you wanted to disable it you would use this name in the  ptah_settings['disable_modules'] registration.

An example::

    import ptah
    
    @ptah.manage.module('rest')
    class RestModule(ptah.manage.PtahModule):
        """
        REST Introspector
        """
        title = 'REST Introspector'

View
----

The module views for the Manage Interface use traversal.  It is important to note that you *do not* have to use ptah.View but you will need to use wrapper so your template will look like the rest of the Manage Interface.  Here is an example, again, from the REST module::

    from pyramid.view import view_config

    @view_config(
        context=RestModule,
        wrapper=ptah.wrap_layout(),
        renderer='ptah.manage:templates/rest.pt')

    class RestModuleView(ptah.View):
        def update(self):
            self.url = self.request.params.get('url','')

Nothing special.  Just a Pyramid view with `wrapper=ptah.wrap_layout()` and you can do whatever you like in that view.
