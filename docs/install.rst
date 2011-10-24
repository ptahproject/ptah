===============
Installing Ptah
===============

Currently Ptah is quite rough around the edges.  virtualenv is the prefered
mode of installation at this time.

Requirements
------------

  * Python 2.7
  
  * git

virtualenv & pip
~~~~~~~~~~~~~~~~

This is recommended for the public.  Read more,  
`installing with virtualenv <https://github.com/ptahproject/ptah/blob/master/docs/virtualenv.rst>`_

buildout
~~~~~~~~

This is not recommended for public.  Skip to next section.

Grab buildout::

  ~$ git clone https://github.com/ptahproject/devel
  
  ~$ cd devel
  
  ~/devel$ python2.7 bootstrap.py -c devel.cfg
  You will see it download setuptools & will create bin directory
  
  ~/devel$ bin/buildout -c devel.cfg
  Go grab some coffee. It will take awhile.
  If you are adventurous you can bin/buildout - c devel-socket.cfg
  which will install the websocket server which `ptah_app` uses.
  
  ~/devel$ bin/paster serve ptah.ini
  Some paster output and it will say listening on port 8080.  Pyramid
  and Ptah are now running.

Logging in
----------

In your browser::

  Goto URL, http://localhost:8080/
  What you are seeing is `ptah_app`.  This is a default Ptah CMS.
  You can sign-in on the upper right hand side.  The default login
  is `admin` with password `12345`.

  The user creation and other bootstrap can be found in python module
  ~/devel/src/devapp/devapp/initialize.py -- we will do better in future.

Management UI
-------------

In your browser (after logging in)::

  Goto URL, http://localhost:8080/ptah-manage
  The `ptah management` UI provide introspection services.  The goal
  is to have a WEB interface for your installation.  We hope for you
  to be able to see latest module updates and do some other fancy
  stuff.  You can think of `ptah-manage` as the unfriendly nerd console.

REST API
--------

Grab curl.  And lets curl Ptah's REST API::

  ~/devel$ curl http://localhost:8080/__rest__/cms/

You will also notice in ~/devel/rest.py there is a module which exercises
the REST API.  It maybe of interest and if your up for hacking on it - go
for it.  We want models, schemas, type, and nearly all facilities to be
exposed automatically when consuming high level APIs of Ptah.

Websocket
---------

This is experimental and no support is offered.  Please do not ask
questions about this functionality.  It will be supported in 1.0 but
not at this time.

If you have greenlets and gevent installed by running
`bin/buidout -c devel-socket.cfg` you will have an extra
script inside of bin called `socket-server`.  You can just
run it::

  ~/devel$ bin/socket-server
  it will spew lots of ugliness onto console.  disregard for now

Once you have the socket server running you can login to Ptah CMS
with 2 separate modern browsers.  Create/edit/delete content in
one browser.  You will notice Growl-style notifications being
displayed in the browser were you did not modify content.

This functionality is currently very primitive but it will be a
core service of Ptah and security will be applied to events.

Conclusion
----------

If you have gotten this far and Ptah hasnt crashed or failed in some way
I am impressed.  We are focusing on documentation, API cleaning, and
test coverage.  There is alot of construction.  If you want to help - you
are more than welcome.  Please do us the following favors:

  * Please do not name a package with the top level ``ptah_``
    namespace.  We would like to formally bless any software with these
    prefixes in a package name.

  * We strongly suggest using the experimental top-level namespace that
    Plone uses. It conotes that your package is released but not something
    you recommend people using.

We are currently looking for UI gurus.
