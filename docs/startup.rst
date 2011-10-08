Pyramid & Ptah Startup
======================

Requirements
------------
You must pass a pyramid Configurator.registry object into 
memphis.config.initialize and  memphis.config.initializeSettings. You can
manually create WSGI App and initialize it or Ptah can perform this for you.

config.initialize
-----------------

This function is found at, memphis.config.initialize

  - inspects all eggs using setuptool.pkg_resources
  - find all memphis-related eggs using setup.py entry_points::
  
          entry_points = {
            'memphis': ['package = your_package'],
          }
        
  - for each memphis egg it is loaded
    memphis.config.loadPackage(memphis-related-egg)
    All configuration has been read and registrations are loaded in memory
    
  - Checks for configuration conflicts

config.initializeSettings
-------------------------

This function, memphis.config.initializeSettings(/path/to/settings.ini)

  - consumes the .ini file and parses it
  - makes all values available in memphis.config.Settings dict
  - notify(memphis.config.ISettingsInitializing)
    - memphis/pyramid related packages who subscribe to pyramid's event channel will get this event.
    - each package can configure itself at this point with environment
  - At this point pyramid and ptah as well as all add-ons will be fully
    configured.  Services available:
    - Query database
    - Send mails
    - See layouts/views/etc.
      
ptah.make_wsgi_app
-------------------

Optional. If you are using ptah.make_wsgi_app some extra features are available:

  - notify(ptah.IAppInitialized, pyramid.Configurator, pyramid.wsgiapp)
  - subscribers can do things such as change database models, add records, etc.
  - add pyramid specific views/configuration.

This function returns a WSGIApp.

I have 2 ways to do register?
-----------------------------
Yes.  But its easier to think about it this way.  Pyramid is a agnostic 
web framework.  Ptah is a application/web framework with opinions. 
Ptah registration revolve around services (uri resolvers, models and a
type system).  These memphis registration's are application specific and
have no such equivilent in Pyramid (nor should they).  

Where is memphis.config used?
-----------------------------
Everywhere.  But you never touch it.  There is always formal API that is defined and (will be( documented.  The internal implementation uses memphis.config implementation.

Some examples:

  - "service" registration, ala. ptah.uri (see ptah_cms.tinfo)
  
  - REST registration, ala. ptah_cms.rest
  
  - Field registration, memphis.form.field
  
  - Ptah App provides "UI Action" to show "Edit, Sharing, etc" actions
  
  - Ptah security: ptah.security.Permission

What is difference in Pyramid?
------------------------------
If you are using Pyramid you will define your own entry-point for paster
which will create Configurator object and load your external packages.

(Will add link to pyramid example).

In ptah you do not need to do this; you subscribe to the IAppInitialized
event and you can add your specific pyramid configurations.

In Ptah there is a single entry-point which will notify subscribers for
initialization.  In Pyramid your entry-points get called directly.  The
convienance of Ptah You
can do the work of Ptah manually; its just added convienance for Ptah
usage. 

Pyramid configuraiton vs. Memphis configuration
-----------------------------------------------
In Pyramid configuration statements such as pyramid.config.add_route, etc
generate Actions (same as memphis).  

Currently Memphis differs in Pyramid in the following ways.

  - Memphis configuration has different information during configuration
  
    - config statements have context (module, line, etc)
    
    - config statements talk about different "services" (ala uri.resolver)
    
    - config statements ALWAYS stay in memory, never thrown away.  We need
      these for Ptah 1.0 when we hope to have add-ons added during runtime
      and possibly removing add-ons during runtime (without restarting).
    
  - Pyramid configuration
  
    - config statements do not have context (but will in 1.4?)
    
    - config statemetns talk about concrete services of *pyramid* ala
      route, views, etc. not high-level application services such as
      model registration.
      
    - config statements will be inspectable but in future but most likely
      thrown away. e.g. pyramid probably has no desire to add config 
      statements at run-time or to "unload" configuration at run-time.

In Memphis there is a 
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
    
    - Without this you could see a new URI resolver registered but you would not know exactly which package was responsible for that registration.
    
    - Another possibility is unloading this configuration.  In future we may have a add-on ecosystem where you will want to "unload" registrations.  
    
  - registeration/apply are runtime features of memphis.config and maybe in future there will be remove registrations.  

More thoughts
-------------
Pyramid is explicit.  Memphis is sort-of implicit and has indirection.  For instance memphis needs to scan packages with the entry-point memphis.  Pyramid would need to expose this functionality for memphis to plugin its own higher-level registration calls (uri, type system, etc).
Also Ptah/memphis reuse memphis.config in a lot of places.  The pattern
of having an public API which advertises the functionality but internally uses the memphis.config implementation - is inspired from Pyramid.