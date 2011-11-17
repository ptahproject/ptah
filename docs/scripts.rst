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

paster
------

There are 2 paster plugins which will be moved to separate entry-points.
Currently bin/paster static

  static - will list all static resource registrations. dump/consolidate all static registraitons.

  templates - bin/paster templates will list all templates registered in the system.

socket-server
-------------
OPTIONAL

if you run with the socketserver configuration this is the startup script which is used for websockets.

develop
-------
OPTIONAL

mr.developer which is used by the Ptah developers to manage their source project.

