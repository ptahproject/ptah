===============
Installing Ptah
===============

Currently Ptah is quite rough around the edges. virtualenv is the prefered
mode of installation at this time.

Requirements
------------

  * Python 2.7

  * git

virtualenv
~~~~~~~~~~

This is the recommend way for people to install Ptah.
Grab a copy of the latest virtualenv.

  * git clone https://github.com/ptahproject/ptah
  * cd ptah; python setup.py develop
  * cd ..; bin/paster create -t ptah101 myapp
  * cd ptah101; python setup.py develop
  * cd ..; bin/paster serve myapp/settings.ini --reload

buildout
~~~~~~~~

This is not recommended for people to install Ptah.
Although many developers really like this approach.

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

  Goto URL, http://localhost:8080/ptah-manage/
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
