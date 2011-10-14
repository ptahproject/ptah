Virtualenv and Pip
==================
virtualenv and pip are convienant ways to install python packages.  

You will need Python 2.7 and git installed on your machine.  

Install virtualenv
------------------

First install virtualenv::

    ~$ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    ~$ python2.7 virtualenv.py --no-site-packages myvirtualenv
    ~$ cd myvirtualenv
    
Create requirements
-------------------

Lets create the `pip` requirements.txt file::

    ~/myvirtualenv$ cat > requirements.txt
    -e git+https://github.com/ptahproject/memphis#egg=memphis
    -e git+https://github.com/ptahproject/ptah.git#egg=ptah
    ^C

Install the requirements
------------------------

Let's run pip's installer to grab all of our software::

     ~/myvirtualenv$ bin/pip install -r requirements.txt
     ... a lot of text while system resolves dependencies and installs software

Create ptah app
~~~~~~~~~~~~~~~

Let's create ptah app with paster::

     ~$ ./bin/paster create -t ptahdemo myapp
     ~$ cd myapp
     ~$ ../bin/python2.7 ./setup.py develop

Start app
~~~~~~~~~

Start paster server::

     ~$ ../bin/paster serve development.ini

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
read up how to use coverage integration.  

Run memphis tests::

    ~$ cd src/memphis
    memphis$ ../bin/python setup.py develop
    memphis$ ../bin/python setup.py test

Run ptah tests::

    ~$ cd src/ptah
    ptah$ ../bin/python setup.py develop
    ptah$ ../bin/python setup.py test

Run myapp tests::

    ~$ cd myapp
    myapp$ ../bin/python setup.py test
