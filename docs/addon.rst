Addon
=====

The addon subsystem allows packages to be installed easily.  This is experimental and should only be used if you are interested in helping with the design of the subsystem.  

Example
-------

The example uses routes only.  It does not use traversal. You can find an example of a addon here:

  - https://github.com/ptahproject/devel/tree/master/addons/devpoll

Overview
--------

All of your configuration will get loaded automatically by defining an entry-point as ptah.  Your addon package will be scanned and all configuration will be visible in Ptah Manage.  If your addon registration succeeds you will see it in Ptah Manage under Addons.  

AppStarting
-----------

The current, crude, method for you to register is to subscribe to the
:py:class:`ptah.config.AppStarting` event.  The event will have an attribute, `config` which will be a Configurator.  You can use the configurator like you normally would.  **DO NOT** commit a transaction in your subscriber; that will happen when someone installs the addon.

More code
---------

Before scaffolding we used this event for application's to insert their
configuration via event listener.  You can find this code here.

  - https://github.com/ptahproject/devel/blob/master/src/devapp/devapp/initialize.py
  
Again, do you not use that code but it gives you example of how your addon can participate if it needs to do something more than register configuration.  Remember by simply being in the addon directory with the entry-point in your setup.py; Ptah will scan all files and include them in (without commiting the configuration transaction) and will be available in the addon module in Ptah Manage.
