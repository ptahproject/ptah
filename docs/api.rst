Ptah API
--------

.. automodule:: ptah

URI
~~~

  .. autofunction:: resolve

  .. autofunction:: resolver

  .. autofunction:: register_uri_resolver

  .. autofunction:: extract_uri_schema
  
  .. autoclass:: UriFactory

Security
~~~~~~~~

  .. autofunction:: authService
  
  .. py:data:: SUPERUSER_URI

  .. autofunction:: auth_checker
  
  .. autofunction:: register_auth_provider

  .. autofunction:: search_principals
  
  .. autofunction:: principal_searcher
  
  .. autofunction:: register_principal_searcher

ACL, Roles, Permissions
~~~~~~~~~~~~~~~~~~~~~~~

  .. autoclass:: ACL
  
  .. autoclass:: ACLsProperty
  
  .. autofunction:: get_acls
  
  .. autoclass:: Role
  
  .. autofunction:: get_roles
  
  .. autofunction:: get_local_roles

  .. autoclass:: Permission
  
  .. autofunction:: get_permissions
  
  .. autofunction:: check_permission

  .. py:data:: Everyone
  
  .. py:data:: Authenticated
  
  .. py:data:: Owner

  .. py:data:: DEFAULT_ACL  

  .. py:data:: NOT_ALLOWED

  .. py:data:: NO_PERMISSION_REQUIRED

  .. autofunction: passwordTool

  .. autofunction: password_changer


Utilities
~~~~~~~~~

  .. autoclass:: Pagination

  .. py:data:: tldata
  
  .. autoclass:: JsonDictType

  .. autoclass:: JsonListType

  .. autofunction:: generate_fieldset
  
  .. autofunction:: build_sqla_fieldset
  


Ptah CMS API
------------

.. automodule:: ptah.cms

Content classes
~~~~~~~~~~~~~~~

  .. autoclass:: Node

  .. autoclass:: Content

  .. autoclass:: Container
     :members: keys, get, items, values, __contains__, __getitem__, __setitem__, __delitem__


Content loading
~~~~~~~~~~~~~~~

  .. autofunction:: load

  .. autofunction:: load_parents


Type system
~~~~~~~~~~~

  .. autofunction:: get_type

  .. autofunction:: get_types

  .. autofunction:: Type

  .. autoclass:: TypeInformation


Application Root/Factory/Policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  .. autoclass:: ApplicationRoot

  .. autoclass:: ApplicationPolicy

  .. autoclass:: ApplicationFactory

Blob api
~~~~~~~~

  .. py:data:: blobStorage

  .. py:class:: IBlob

  .. py:class:: IBlobStorage

Content schema
~~~~~~~~~~~~~~

  .. py:class:: ContentSchema

  .. py:class:: ContentNameSchema


Permissions
~~~~~~~~~~~

  .. py:data:: View

  .. py:data:: AddContent

  .. py:data:: DeleteContent

  .. py:data:: ModifyContent

  .. py:data:: ShareContent

  .. py:data:: NOT_ALLOWED

  .. py:data:: ALL_PERMISSIONS


Events
~~~~~~

  .. autoclass:: ContentEvent

  .. autoclass:: ContentCreatedEvent

  .. autoclass:: ContentAddedEvent

  .. autoclass:: ContentMovedEvent

  .. autoclass:: ContentModifiedEvent

  .. autoclass:: ContentDeletingEvent

