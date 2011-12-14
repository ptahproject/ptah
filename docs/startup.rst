Pyramid & Ptah Startup
======================

config.ptah_initialize
----------------------

The Pyramid Configurator must have commit() called *before* 
config.ptah_initalize() is called on the Configurator.  ptah_initialize
does extra work, for instance; setting up the authentication service and
calling ptah._init_settings (initialize settings).

This function is found at, ptah.ptah_initialize.