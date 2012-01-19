Ptah
====

Ptah is a fast, fun, open source high-level Python web development environment. Ptah is built on top of the Pyramid web framework.  Ptah's goal is to make developing interactive web sites and applications fun.  Ptah aims to fill a void in the Pyramid eco-system, a "full stack" environment which is well integrated and provides opinions (forms, management ui, models, etc).

Ptah is loosely affiliated with the Pyramid, Django, Drupal and Zope/Plone communities.  

Most documentation requires Ptah 0.3 or greater.

You can read the `ptah` documentation on-line at 
`http://ptahproject.readthedocs.org <http://ptahproject.readthedocs.org/en/latest/index.html>`_.

Requirements
------------

- Python 2.6+ or Python 3.2+

- virtualenv

Note for Windows Users
----------------------

On Windows virtualenv/bin will be virtualenv/Scripts besides this difference everything else below is the same.


Grab the release
----------------

If you do not want to faff about with source, cloning repos, etc.  Just grab the latest released version of ptah. 

  $ /path/to/virtualenv/bin/pip install ptah


Ptah from source
----------------

If you want the latest and greatest you need to grab code from source.  

clone `ptah` from github and then install it::

  $ /path/to/virtualenv/bin/python setup.py develop

then run the tests::

  $ /path/to/virtualenv/bin/python setup.py test


An empty project
----------------

Let's generate a empty project using the `ptah_starter` scaffolding. You can start from there::

  /path/to/virtualenv $ bin/pcreate -t ptah_starter myapp
  /path/to/virtualenv $ cd myapp
  /path/to/virtualenv/myapp $ ../bin/python setup.py develop
  /path/to/virtaulenv/myapp $ ../bin/pserve settings.ini --reload

Open your browser to http://localhost:6543/ if you want examples that do more such as demonstrating editing models and authentication.  Check out the examples.
  

Examples
--------

There are several example applications ready for you to install and see Ptah in action.  You can find them in the `examples` repository at github.

https://github.com/ptahproject/examples


Support and Documentation
-------------------------

Ptahproject google groups/mailing list, `Ptahproject Google Groups <http://groups.google.com/group/ptahproject/>`_

On irc, use the freenode network and find us on channels, #ptahproject and #pyramid.

Documentation can be found in `docs` directory.  You can also see it online at `http://ptahproject.readthedocs.org/  <http://ptahproject.readthedocs.org/en/latest/index.html>`_

Report bugs at `Ptahproject @ Github <https://github.com/ptahproject/ptah/issues>`_


Known Issues
------------

On some versions of Ubuntu you may get Python 2.7 exiting stating it has "Aborted." There is a bug in ctypes on that particular Ubuntu platform.


License
-------

Ptah is offered under the BSD3 license.


Authors
-------

Ptah is written by Python enthusiasts who refuse to compromise.
