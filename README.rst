Ptah
====

Ptah is a fast, fun, open source high-level Python web development environment.
Ptah is built on top of the Pyramid web framework.  Ptah's goal is to make 
developing interactive web sites and applications fun. 

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
          
You may ask, Why the duplication of nested folders?  It's how Python packages 
are structured.

On Windows you will have a venv/Scripts directory not a venv/bin directory. 

Lets do the needful::

  $ curl -k -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
  $ python2.7 virtualenv.py --no-site-packages venv
  $ cd venv
  venv$ bin/pip install -e git://github.com/ptahproject/ptah.git#egg=ptah
  venv$ cd src/ptah
  venv/src/ptah$ ../../bin/python setup.py develop
  venv/src/ptah$ cd ..  
  
Use paster to create your application.  The default username and password are:
**admin** as login and **12345** as password::

  venv/src$ ../bin/paster create -t ptahdemo myapp
  venv/src$ cd myapp
  venv/src/myapp$ ../../bin/python setup.py develop
  
Start application via Paster::

  venv/src/myapp$ cd ../..
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

Ptah is written by Python enthusiasts who do not want compromise.
