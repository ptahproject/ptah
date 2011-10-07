Static assets
=============

Reasons why memphis static assets exists.

 * Registration executed before pyramid configuration object is constructed.

 * All static assets available under one base url, for example:
   
   http://ptahproject.org/static/...

 * It is possible to dump static assets from all package into one 
 filesystem directory. And then serve static assets from external webserver.


Registration
------------

Example::

  from memphis import view

  view.static('bootstrap', 'memphis.view:static/bootstrap')

Thats it, everything from `memphis/view/static/bootstrap` directory available
as `http://localhost:8080/static/bootstrap/` url.
