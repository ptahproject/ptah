Virtualenv and Pip
==================
virtualenv and pip are convienant ways to install python packages.  

You will need Python 2.7 and git installed on your machine.  

Install virtualenv
------------------

You need 1.6.4 of virtualenv or greater for Git support.  
use your existing virtualenv.  It takes < 15 seconds to grab it. 

install virtualenv::

 ~$ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
 ~$ python2.7 virtualenv.py --no-site-packages venv
 ~$ cd venv

install ptah::

 ~/venv$ bin/pip install -e git+https://github.com/ptahproject/ptah.git#egg=ptah
 ~/venv$ cd src/ptah
 ~/venv/src/ptah$ ../../bin/python setup.py develop
 
Create ptah addon 
~~~~~~~~~~~~~~~~~

Let's create ptah addon with paster::

 ~/venv/src/ptah$ cd ..
 ~/venv/src$ ../bin/paster create -t ptahdemo myapp
 ~/venv/src$ cd myapp
 ~/venv/src/myapp$ ../../bin/python2.7 setup.py develop


Start app
~~~~~~~~~

Start paster server::

 ~/venv$ bin/paster serve development.ini

Login
~~~~~

A default user is created for you. login: admin and password: 12345

Open your browser to see Ptah App, http://localhost:6543/

You can see Ptah Manage, http://localhost:6543/ptah-manage/

These are 2 separate wsgi apps.  They are both optional.  The "DT" tab
on the right hand side of the screen is the Debug Toolbar from Pyramid.

Run Tests
~~~~~~~~~

We use the `nose` test runner to collect which tests to run.  You can
read up how to use coverage integration.  This is standard python usage
of the the nose library; nothing fancy.

Run ptah tests::

    ~$ cd src/ptah
    ptah$ ../bin/python setup.py develop
    ptah$ ../bin/python setup.py test

Run myapp tests::

    ~$ cd myapp
    myapp$ ../bin/python setup.py test

Summary
~~~~~~~

Look inside myapp/__init__.py and you will see the application 
startup configuration.
