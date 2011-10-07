Pyramid & Ptah Startup
======================

Requirements
------------
You or ptah must create a Pyramid Configurtor

config.initialize
-----------------
memphis.config.initialize
    - inspects all eggs using setuptool.pkg_resources
    - find all memphis-related eggs (entry-point: memphis)
    - for each memphis egg
      - memphis.config.loadPackage(memphis-related-egg)
    All configuration has been read and registrations are loaded in memory
  - Checks for configuration conflicts if ok, apply changes

config.initializeSettings
-------------------------
memphis.config.initializeSettings(/path/to/settings.ini)
    - consumes the .ini file and parses it
    - makes all values available in memphis.config.Settings dict
    - notify(memphis.config.ISettingsInitializing)
      - memphis/pyramid related packages who subscribe to pyramid's
        event channel will get this event.
      - each package can configure itself at this point with environment
  - At this point pyramid and ptah as well as all add-ons will be fully
    configured.  Services available:
      - Query database
      - Send mails
      - See layouts/views/etc.
      
ptah.make_wsgi_app
-------------------
Optional. If you are using ptah.make_wsgi_app some extra features are available:
    - notify(ptah.IWSGIAppInitialized, pyramid.configuration, pyramid.app)
    - subscribers can do things such as change database models, add records, etc.
    - add pyramid specific views/configuration.
    returns a WSGIApp

What is difference in Pyramid?
------------------------------
If you are using Pyramid you will define your own entry-point for paster
which will create Configurator object and load your external packages.
In ptah you do not need to do this; you subscribe to the IWSGIAppInitialized
event and you can add your specific pyramid configurations.

In Ptah there is a single entry-point which will notify subscribers for
initialization.  In Pyramid your entry-points get called directly.  You
can do the work of Ptah manually; its just added convienance for Ptah
usage. 

Pyramid configuraiton vs. Memphis configuration
-----------------------------------------------
In Pyramid you can "defer" your configuration.  In Memphis there is a 
more formal 2 stage configuration, registration stage and apply stage.
It loads all packages and can be introspected and then a applying
the configuration to the environment.  Why?  An example:

  URI implementaiton is a dictionary which maps the uri scheme / key
to resolver callable.  {'crowd+user':ptah.crowd.userProvider}.  If an
add-on package defines an additional URI resolver, what will happen when
we load the external package:
  - It does not immediately load the resolver into the main dictionary
  - memphis will have the registration and can check for conflict as well
    as have access to all API registrations for the add-on package.
  - At this point you can control whether or not you want to apply the
    add-on registrations.  
  - Because memphis has the configuration object and its a separate step
    to apply; memphis.config KNOWS which add-on is repsonsible for the
    implementation.  
    - Without this you could see a new URI resolver registered but you
      would not know exactly which package was responsible for that 
      registration.
    - Another possibility is unloading this configuration.  In future
      we may have a add-on ecosystem where you will want to "unload"
      registrations.  
  - registeration/apply are runtime features of memphis.config and maybe
    in future there will be remove registrations.  
