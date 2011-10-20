Ptah CMS
========

Ptah is a fast, fun, open source high-level Python web framework. It's prime 
goal is to make developing interactive web applications and web sites which 
require security fun and a lot easier.

Ptah is loosely affiliated with the Pyramid, Django, Drupal and Zope/Plone communities.

Install
-------

You will need git, python 2.7 and a new version of virtualenv.  Before we start
lets review what the structure will look like after you complete the 
instructions::

  venv/
    Include/
    Lib/
      site-packages/
    bin/
      python
      pip
      paster
    src/
      ptah/
        setup.py
        ptah/
        docs/
      myapp/
        setup.py
        development.ini
        myapp/
          

Why the duplication in nested folders?  It's how Python egg's work.

Lets do the needful::

  $ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
  $ python2.7 virtualenv.py --no-site-packages venv
  $ cd venv
  venv$ bin/pip install -e git+https://github.com/ptahproject/ptah.git#egg=ptah
  venv$ cd src/ptah
  venv/src/ptah$ ../../bin/python2.7 setup.py develop
  venv/src/ptah$ cd ..  
  
Use paster to create scaffolding::

  venv/src$ ../bin/paster create -t ptahdemo myapp
  venv/src$ cd myapp
  venv/src/myapp$ ../../bin/python2.7 setup.py develop

Start application via Paster::

  venv$ bin/paster serve src/myapp/development.ini --reload

Login by opening your web browser to http://localhost:6543 with credentials,
login: admin and password: 12345

You can see more information how your App boostraps by looking at myapp/__init__.py

Support and Documentation
-------------------------

Use github until `Ptah Project website <http://ptahproject.org/>`_ is online.

Documentation can be found in ptah/docs directory.

You can ask for help on #pyramid.

License
-------

Ptah is offered under the BSD3 license included in all packages.

Authors
-------

Ptah is written by Python enthusiasts who do not want to compromise.
