Scripts and Entry Points
========================

There are a few scripts which virtualenv or buildout will generate for you when
using Ptah.  In the future we will not use paster but use entry-points which will
be callable.

settings
--------

  bin/settings - list of all settings available in the system.  These can be
  overridden in your .ini settings file.  Put your settings under [DEFAULT].

  bin/settings dump - output all default settings into a target .ini file
