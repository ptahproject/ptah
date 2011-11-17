Ptah
====

Ptah is a fast, fun, open source high-level Python web development environment. Ptah is built on top of the Pyramid web framework.  Ptah's goal is to make developing interactive web sites and applications fun.

Ptah is loosely affiliated with the Pyramid, Django, Drupal and Zope/Plone communities.

Requirements
------------

You will need **git**, **python 2.7** and a new version of **virtualenv**.

Install
-------
Before we start lets review what the structure will look like after you complete the instructions::

  venv/
    Include/
    Lib/
      site-packages/
    bin/
      python
      pip
      paster
    ptah/
      setup.py
      ptah/
      docs/
    myapp/
      setup.py
      development.ini
      myapp/

On Windows you will have a venv/Scripts directory not a venv/bin directory.

Lets do the needful::

  $ curl -k -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
  $ python2.7 virtualenv.py --no-site-packages venv
  $ cd venv
  venv$ git clone git://github.com/ptahproject/ptah.git
  venv$ cd ptah
  venv/ptah$ ../bin/python setup.py develop

If you like tests, run the tests::

  venv/ptah$ ../bin/python setup.py test

Ptah 101, the Basics
--------------------

The first scaffolding, ptah101, provides an example of the ptah manage facility, as well, how the form machinery works.

Use paster to create a ptah101 application::

  venv/ptah$ cd ..
  venv$ bin/paster create -t ptah101 myapp101

Start application via Paster::

  venv$ cd myapp101
  venv/myapp101$ ../bin/paster serve settings.ini --reload

Ptah 102, Models
----------------

The second scaffold, ptah102, provides an example of using a sqlalchemy model and enables more features of the management ui.

Use paster to create a ptah102 application::

  venv$ bin/paster create -t ptah102 myapp102

Start application via Paster::

  venv$ cd myapp102
  venv/myapp102$ ../bin/paster serve settings.ini --reload

Ptah 201, Security
------------------

The third scaffold adds security and demonstrates creating your own user system and protecting a resource with security (ptah-manage).

Use paster to create a ptah201 application::

  venv$ bin/paster create -t ptah201 myapp201

Start application via Paster::

  venv$ cd myapp201
  venv/myapp201$ ../bin/paster serve settings.ini --reload

Ptah 301, a CMS
---------------

This is a fairly sophisticated example which is nearly a mini-CMS. It demonstrates nearly all the features of Ptah but is probably overwhelming for newbies.

Use paster to create a mini-cms application::

  venv$ bin/paster create -t ptah301 myapp301
  venv$ cd cmsapp

Start application via Paster::

  venv/cmsapp$ ../bin/paster serve development.ini --reload

Login by opening your web browser to http://localhost:6543/ with credentials, login **admin** and password **12345**

Support and Documentation
-------------------------

Use github until website is online.

Documentation can be found in ptah/docs directory.

Ptahproject google groups/mailing list, `Ptahproject Google Groups <http://groups.google.com/group/ptahproject/>`_

On irc, use the freenode network and find us on channels, #ptahproject and #pyramid.

Report bugs at `Ptahproject @ Github <https://github.com/ptahproject/ptah/issues>`_

Known Issues
------------

On some versions of Ubuntu you may get Python exiting stating it has "Aborted." There is a bug in ctypes importing endian module.

License
-------

Ptah is offered under the BSD3 license.

Authors
-------

Ptah is written by Python enthusiasts who refuse to compromise.