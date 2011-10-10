Memphis config  API
-------------------

.. automodule:: memphis.config

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

  .. autofunction:: initializeSettings

  .. autofunction:: registerSettings

Settings events
~~~~~~~~~~~~~~~

  .. autoclass:: SettingsInitialized

  .. autoclass:: SettingsInitializing

  .. autoclass:: SettingsGroupModified

  .. autoclass:: ApplicationStarting
