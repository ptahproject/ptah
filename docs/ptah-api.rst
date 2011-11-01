Ptah Public API
---------------

.. automodule:: ptah

URI
~~~

  .. autofunction:: resolve

  .. autofunction:: register_uri_resolver(schema, resolver, title='', description='')

  .. autofunction:: extract_uri_schema

  .. autoclass:: UriFactory
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

  .. autoclass:: Role(name, title, description='')

  .. autofunction:: get_local_roles

  .. autofunction:: get_roles


Permissions
~~~~~~~~~~~

  .. py:data:: Permissions
     
     Permissions dictionary contains all registered permissions in the system.

  .. autofunction:: Permission

  .. autofunction:: check_permission


misc
~~~~

  .. autofunction:: make_wsgi_app

  .. autofunction:: ptah_init
