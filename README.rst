Ptah
====

Ptah is a fast, fun, open source high-level Python web development environment.
Ptah is built on top of the Pyramid web framework.  Ptah's goal is to make 
developing interactive web sites and applications fun. 

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
          
You may ask, Why the duplication of nested folders?  It's how Python packages are structured.

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

Use paster to create **your own application**.  The default username is **admin** and password is **12345**.  Check myapp/__init__.py for more information::

  venv/ptah$ cd ..
  venv$ bin/paster create -t ptah101 myapp
  venv$ cd myapp
  venv/myapp$ ../bin/python setup.py develop
  
Start application via Paster::

  venv/myapp$ cd ..
  venv$ bin/paster serve myapp/settings.ini --reload

Login by opening your web browser to http://localhost:6543/ with credentials, login **admin** and password **12345**

You should read the source of myapp, after all it is your application.  A good place to start is myapp/__init__.py

Support and Documentation
-------------------------

Use github until `Ptah Project website <http://ptahproject.org/>`_ is online.

Documentation can be found in ptah/docs directory.

Over email, use ptahproject google groups, `Ptahproject Google Groups <http://groups.google.com/group/ptahproject/>`_

On irc, use the freenode network and find us on channeld, #ptahproject and #pyramid.

License
-------

Ptah is offered under the BSD3 license.

Authors
-------

Ptah is written by Python enthusiasts who refuse to compromise.
