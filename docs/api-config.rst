Ptah config  API
----------------

.. automodule:: ptah.config

  .. py:data:: registry

     Active components registry

  .. autofunction:: initialize

  .. autofunction:: notify


Directives
~~~~~~~~~~

  .. autofunction:: event

  .. autofunction:: action

  .. autofunction:: adapter

  .. autofunction:: subscriber


Settings
~~~~~~~~

  .. autofunction:: initialize_settings

  .. autofunction:: register_settings

Settings events
~~~~~~~~~~~~~~~

  .. autoclass:: SettingsInitialized

  .. autoclass:: SettingsInitializing

  .. autoclass:: SettingsGroupModified

  .. autoclass:: ApplicationStarting
