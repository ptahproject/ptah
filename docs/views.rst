Views and Layouts
=================

Ptah views are Pyramid views.  Familiarize yourself with Pyramid views (URL).  The decoration for memphis.views is different than pyramid but this is because its internally consistent (using memphis.config).  Layouts are Ptah specific.

Views
-----
Really no different at all in Pyramid other than configuration statements. There are 2 ways to customize a view.  Override the entire View or you can override the template on a view.

View Templates
~~~~~~~~~~~~~~
An additional feature is that templates which are bound to views can be overridden separately from their views.  You can also list all templates, where it was defined and where it exists on the filesystem.

Template support is currently only Chameleon but its very easy to reimplement this support for Jinja and other template engines.

Layouts
-------
This concept provides ability to nest different HTML generation facilities to create a web page.  You do not have to use Layouts.  You can (and should) use your native template engines macro/inheritance facilities.  You do not have to use/learn Layouts to use Ptah.  Ptah App does use this facility.

Ptah App and Ptah Manage both use Layouts to generate their structure and render full pages.  In reality you will just use a Layout or define your own.  Knowing the ins and outs may not be very interesting to you.  

Layout in Ptah is based on the context in which the template is being rendered.  It is not really a replacement for template composition available inside of the different template implementations.  It is more 

Comparison with PT/METAL
~~~~~~~~~~~~~~~~~~~~~~~~
TODO - REMEMBER YOU CAN STILL USE NATIVE TEMPLATE COMPOSITION

Comparison with Jinja Inheritance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO - REMEMBER YOU CAN STILL USE NATIVE TEMPLATE COMPOSITION

Comparison with Mako
~~~~~~~~~~~~~~~~~~~~
TODO - REMEMBER YOU CAN STILL USE NATIVE TEMPLATE COMPOSITION

Static Resources
----------------

memphis static resources always are served from /static/ in your URL.  This "static resource prefix" is configurable but the idea is that all static assets are served the same way.  Whether you want it to be /static/ or /assets/ all resources are locatable through this prefix.

since memphis supports this configuration directive for static resources its also possible to introspect them keeping their identity.  it is core behavior to know where a given resource is defined in the code base.

lastly there is additional funcitonality which allows the framework to consolidate all of the static resources into a set of files/folders which can be served from a different server.  e.g.  before production code push you can "re-dump" all static assets and move them to nginx.

Libraries
---------
If you want to include something in the HEAD; libraries are used for this.

Formatters
----------
Convienance functions which provide helpers to display information.  The registered formatters are callable.  They are located in memphis.view.format. An example of this would be for localization, in your settings.ini file you can specify the date format to be displayed.  So if you use the view.format.date_short(datetime.date(2011, 12,12)) the resulting format will be based on the localization settings file.

The goal is to have consistent format for values across a variety of applications, e.g. datetime, timezone, currency.

Messages
--------
This is a reimplementation of pyramid flashmessages.  This could probably be removed.

Pagelets
--------
We will either rename this or remove it.  I hate this name.
