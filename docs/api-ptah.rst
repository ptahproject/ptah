Ptah Public API
---------------

.. automodule:: ptah

URI
~~~

  .. autofunction:: resolve

  .. autofunction:: resolver

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
  
  .. autofunction:: get_acls

  .. autoclass:: IACLsAware


Roles
~~~~~

  .. autoclass:: Role(name, title, description='')

  .. autofunction:: get_local_roles

  .. autofunction:: get_roles

  .. autoclass:: IOwnersAware

  .. autoclass:: ILocalRolesAware

  .. py:data:: Everyone
  
  .. py:data:: Authenticated
  
  .. py:data:: Owner


Permissions
~~~~~~~~~~~

  .. py:data:: Permissions
     
     Permissions dictionary contains all registered permissions in the system.

  .. autofunction:: Permission

  .. autofunction:: get_permissions
  
  .. autofunction:: check_permission

  .. py:data:: DEFAULT_ACL  

  .. py:data:: NOT_ALLOWED

  .. py:data:: NO_PERMISSION_REQUIRED


Security
~~~~~~~~

  .. py:data:: auth_service

  .. py:data:: SUPERUSER_URI

  .. autofunction:: auth_checker

  .. autofunction:: auth_checker

  .. autofunction:: register_auth_provider

  .. autofunction:: search_principals

  .. autofunction:: principal_searcher

  .. autofunction:: principal_searcher

  .. autofunction:: register_principal_searcher


Password utils
~~~~~~~~~~~~~~

  .. py:data:: pwd_tool

  .. autofunction:: password_changer

  .. py:data:: PWD_CONFIG


Utilities
~~~~~~~~~

  .. autoclass:: Pagination

  .. py:data:: tldata
  
  .. autoclass:: JsonDictType

  .. autoclass:: JsonListType

  .. autofunction:: generate_fieldset
  
  .. autofunction:: build_sqla_fieldset
  
  .. autofunction:: rst_to_html


UI Actions
~~~~~~~~~~

  .. autofunction:: uiaction

  .. autofunction:: list_uiactions


misc
~~~~

  .. autofunction:: make_wsgi_app

  .. autofunction:: ptah_initialize
