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
    Chameleon == 2.4.5
    zope.interface >= 3.8.0
    -e git+https://github.com/Pylons/colander.git#egg=colander
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
