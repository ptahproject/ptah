Ptah Public API
---------------

.. automodule:: ptah

URI
~~~

  .. autofunction:: resolve

  .. autofunction:: registerResolver(schema, resolver, title='', description='')

  .. autofunction:: extractUriSchema

  .. autoclass:: UriGenerator
     :members: __call__


ACL
~~~

  .. py:data:: ACLs

     ACLs dictionary contains all registered acl maps in the system.

  .. autoclass:: ACL
     :members:

  .. autoclass:: ACLsProperty


Roles
~~~~~

  .. py:data:: Roles

     Roles dictionary contains all registered roles in the system.

  .. autoclass:: Role(name, title, description='')

  .. autofunction:: LocalRoles


Permissions
~~~~~~~~~~~

  .. py:data:: Permissions
     
     Permissions dictionary contains all registered permissions in the system.

  .. autofunction:: Permission

  .. autofunction:: checkPermission


misc
~~~~

  .. autofunction:: make_wsgi_app

  .. autofunction:: initialize

  .. autoclass:: AppInitialized
