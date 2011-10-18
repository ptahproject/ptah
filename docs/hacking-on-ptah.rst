hacking
=======

here are some example workflows you can use to hack on ptah and your own 
component.  git, curl, python2.7 and newer than 1.6.4 version of virtualenv.

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
 ~/workspace/src/ptah $ cd ..
 ~/workspace/src $ ../bin/paster create -t ptahdemo mypackage
 ~/workspace/src $ cd mypackage
 ~/workspace/src/mypackage $ ../../bin/python setup.py develop

You are done, now start paster::

 $ ~/workspace/bin/paster serve ~/workspace/src/mypackage/development.ini --reload

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

Developing a component in buildout
----------------------------------

After running buildout::

  ~ $ cd src
  ~ $ bin/paster create -t ptahdemo $yourcomponent

edit devel.cfg [sources] section and add
yourcomponent = fs yourcomponent

re-run bin/buildout -c devel.cfg

bin/paster serve ptah.ini --reload

and you will ptah running with your component.
you can move yourcomponent = git git@github.com:/yourcomponent/yourcomponent.git later
