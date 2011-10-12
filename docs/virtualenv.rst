Virtualenv and Pip
==================
virtualenv and pip are convienant ways to install python packages.  

You will need Python 2.7 and git installed on your machine.  

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
    Chameleon <= 2.4.5
    -e git+https://github.com/Pylons/colander.git#egg=colander
    -e git+https://github.com/ptahproject/memphis#egg=memphis
    -e git+https://github.com/ptahproject/ptah.git#egg=ptah
    ^C

Create directories
~~~~~~~~~~~~~~~~~~

Create directory where sqlite will store its file.

    ~/myvirtualenv$ mkdir var

Create .ini file
~~~~~~~~~~~~~~~~

Until we get paster rolling, lets manually create .ini file::

    ~/myvirtualenv$ cat > ptah.ini
  
    [DEFAULT]
    # auth
    auth.policy = auth_tkt
    auth.secret = secret-ptah!
    # session settings
    session.type = file
    session.data_dir = %(here)s/var/sessions/data
    session.lock_dir = %(here)s/var/sessions/lock
    session.key = ptahsession
    session.secret = ptahsecret
    # mailer settings
    mail.host = localhost
    mail.port = 25
    mail.queue_path = None
    mail.default_sender = Ptah <info@ptahproject.org>
    mail.debug = true
    # sqlalchemy
    sqla.url = sqlite:///%(here)s/var/db.sqlite
    # custom templates
    template.custom = 
    template.chameleon_reload = true
    # ptah
    ptah.managers.0 = *
    # settings file
    settings = %(here)s/var/settings.cfg

Create Module
~~~~~~~~~~~~~

  ~/myvirtualenv$ curl -O https://raw.github.com/ptahproject/devel/master/start5.py > helloptah.py

Install the requirements
------------------------

Let's run pip's installer to grab all of our software::

  ~/myvirtualenv$ bin/pip install -r requirements.txt
  ... a lot of text while system resolves dependencies and installs software

Starting Ptah
-------------
  
  ~/myvirtualenv$ bin/python helloptah.py ptah.ini

Conclusion
----------

You can goto Ptah Manage, http://localhost:8080/ptah-manage/ and login. 
helloptah.py contains the user/password creation routine. login `admin`
and password `12345`.  

You can see a Ptah Application, http://localhost:8080/ and create content.
