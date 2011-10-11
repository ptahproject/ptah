Virtualenv and Pip
==================
This does not work - check back in future..

virtualenv and pip are convienant ways to install python packages.  This how-to is incomplete and desires your help.  Please help it.  You will need Python 2.7 and git installed on your machine.  

Install virtualenv
------------------

First install virtualenv::

  ~$ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
  ~$ python2.7 virtualenv myvirtualenv
  ~$ cd myvirtualenv

Create requirements
-------------------

Lets create the `pip` requirements.txt file::

  ~/myvirtualenv$ cat > requirements.txt
  git+https://github.com/Pylons/colander.git#egg=colander
  git+https://github.com/ptahproject/memphis#egg=memphis
  git+https://github.com/ptahproject/ptah.git#egg=ptah
  git+https://github.com/ptahproject/ptah_cms.git#egg=ptah_cms
  git+https://github.com/ptahproject/ptah_app.git#egg=ptah_app
  ^C

Install the requirements
------------------------

Let's run pip's installer to grab all of our software::

  ~/myvirtualenv$ bin/pip install -r requirements.txt
  ... a lot of text while system resolves dependencies and installs software

Starting Ptah
-------------

Let's create a helloptah.py file and run it::

  ~/myvirtualenv$ curl -O https://raw.github.com/ptahproject/devel/master/start2.py > hello_ptah.py
  
  ~/myvirtualenv$ python hello_ptah.py
