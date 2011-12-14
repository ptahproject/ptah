Ptah
====

Ptah is a fast, fun, open source high-level Python web development environment. Ptah is built on top of the Pyramid web framework.  Ptah's goal is to make developing interactive web sites and applications fun.  Ptah aims to fill a void in the Pyramid eco-system, a "full stack" environment which is well integrated and provides opinions (forms, management ui, models, etc).

Ptah is loosely affiliated with the Pyramid, Django, Drupal and Zope/Plone communities.

Requirements
------------

- Python 2.7+ or Python 3.2+, we use collections.OrderedDict

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
  
Examples
--------

There are several example applications ready for you to install and see Ptah in action.  You can find them in the `examples` repository at github.

https://github.com/ptahproject/examples

Support and Documentation
-------------------------

Ptahproject google groups/mailing list, `Ptahproject Google Groups <http://groups.google.com/group/ptahproject/>`_

On irc, use the freenode network and find us on channels, #ptahproject and #pyramid.

Documentation can be found in `docs` directory.  You can also see it rendered at `ptahproject.readthedocs.org  <http://ptahproject.readthedocs.org/en/latest/index.html>`_

Report bugs at `Ptahproject @ Github <https://github.com/ptahproject/ptah/issues>`_

Known Issues
------------

On some versions of Ubuntu you may get Python exiting stating it has "Aborted." There is a bug in ctypes on that particular Ubuntu platform.

License
-------

Ptah is offered under the BSD3 license.

Authors
-------

Ptah is written by Python enthusiasts who refuse to compromise.