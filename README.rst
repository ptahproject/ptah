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

  venv/myapp$ ../bin/paster serve settings.ini --reload

Login by opening your web browser to http://localhost:6543/ with credentials, login **admin** and password **12345**

You should read the source of myapp, after all it is your application.  A good place to start is myapp/__init__.py

Sophisticated App
-----------------

Ptah101 scaffold generates a simple application which has an example form, view, a model called Link.  Ptah101 is meant to get your feet wet.  There is a more sophisticated example in the Ptah301 scaffold.  If you have not written a Pyramid application and/or you are not familiar with traversal do not attempt to use Ptah301.  

Let's create a new application & install it using ptah301 scaffold::

  venv$ bin/paster create -t ptah301 cmsapp
  venv$ cd cmsapp
  venv/cmsapp$ ../bin/python setup.py develop

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
