Ptah CMS
========

Ptah is a fast, fun, open source Python web CMS. It's prime directive is to
make developing interactive web applications which require security easier.

Ptah is loosely affiliated with the Pyramid, Django, Drupal and Zope/Plone communities.

Install
-------

You will need git, python 2.7 and a new version of virtualenv.

  $ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
  $ python2.7 virtualenv.py --no-site-packages myvirtualenv

Create a requirements.txt file which contains the following two lines::

  -e git+https://github.com/ptahproject/memphis#egg=memphis
  -e git+https://github.com/ptahproject/ptah.git#egg=ptah

Run pip install::

  $ ../bin/pip install -r requirements.txt

Use paster to create scaffolding::

  $ ../bin/paster create -t ptahdemo myapp
  $ cd myapp
  $ ../bin/python2.7 setup.py develop

Run the tests::

  $ ../bin/python2.7 setup.py test
  
Start application via Paster::

  $ ../bin/paster serve development.ini

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
