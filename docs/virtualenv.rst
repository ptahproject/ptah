Virtualenv
==========
virtualenv is a convienant way to install python packages.  

You will need Python 2.7 and git installed on your machine.  

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
