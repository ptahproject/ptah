hacking
=======

Some developers use `virtualenv` and others use `buildout`.

virtualenv
==========

Grab latest virtualenv, clone ptah into new environment, src directory, use
paster to create a package for your software.

Issue these commands::

 ~ $ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
 ~ $ python2.7 virtualenv.py --no-site-packages workspace
 ~ $ mkdir workspace/src
 ~ $ cd workspace/src
 ~/workspace/src $ git clone git@github.com:ptahproject/ptah.git
 ~/workspace/src $ cd ptah
 ~/workspace/src/ptah $ ../../bin/python2.7 setup.py develop
 ~/workspace/src/ptah $ ../../bin/python2.7 setup.py test

Then you can clone the examples repository and run those to see an application
built using Ptah.

buildout
========

The commands::

  ~ $ git clone github.com/ptahproject/devel
  ~ $ cd devel
  ~ $ python2.7 bootstrap.py -d -c devel.cfg
  ~ $ bin/buildout -c develop.cfg
  ~ $ bin/paster serve ptah.ini --reload

edit devel.cfg and change [sources] section::

 [sources]
 ptah = git git@github.com:myusername/ptah.git

if you delete src/ptah and clone ptah and re-run buildout; you will
be ready to hack

