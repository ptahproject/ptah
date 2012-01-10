ptah
----

.. automodule:: ptah


URI
~~~

  .. autofunction:: resolve

  .. autoclass:: resolver
     :members: register, pyramid

  .. autofunction:: extract_uri_schema

  .. autoclass:: UriFactory
     :members: __call__

Snippet
~~~~~~~
Snippet is very similar to pyramid view.
It doesnt availble with pyramid traversing. It doesnt have security.

  .. autoclass:: snippet()
     :members: register

  .. autofunction:: render_snippet

Layout
~~~~~~

  .. autoclass:: layout()
     :members: register, pyramid

  .. autofunction:: wrap_layout

Library
~~~~~~~

  .. autofunction:: library
  
  .. autofunction:: include
  
  .. autofunction:: render_includes

Settings
~~~~~~~~

  .. autofunction:: get_settings

  .. autofunction:: ptah.settings.init_settings

  .. autofunction:: register_settings

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

  .. autofunction:: Permission

  .. autofunction:: get_permissions
  
  .. autofunction:: check_permission

  .. py:data:: DEFAULT_ACL  

  .. py:data:: NOT_ALLOWED

  .. py:data:: NO_PERMISSION_REQUIRED


Security
~~~~~~~~

  .. py:data:: auth_service

     Instance of :py:class:`ptah.authentication.Authentication` class.

  .. py:data:: SUPERUSER_URI
    
    System user uri. Permission check always passes for user user. 
    It is possible to use it as effective user:

    .. code-block:: python

        ptah.auth_service.set_effective_user(ptah.SUPERUSER_URI)
      
    This allow to pass security checks for any user.

  .. autofunction:: auth_checker

  .. autoclass:: auth_provider
     :members: register

  .. autofunction:: search_principals

  .. autoclass:: principal_searcher
     :members: register


Password utils
~~~~~~~~~~~~~~

  .. py:data:: pwd_tool

     Instance of :py:class:`ptah.password.PasswordTool` class

  .. autoclass:: ptah.password.PasswordTool
     :members:

  .. autoclass:: password_changer
     :members: pyramid


Utilities
~~~~~~~~~

  .. autofunction:: get_base
  
  .. autofunction:: get_session
  
  .. autofunction:: reset_session

  .. autoclass:: Pagination

  .. py:data:: tldata
  
  .. autoclass:: JsonDictType

  .. autoclass:: JsonListType

  .. autofunction:: generate_fieldset
  
  .. autofunction:: build_sqla_fieldset
  
  .. autofunction:: rst_to_html
 
     
Status messages
~~~~~~~~~~~~~~~

  .. autofunction:: add_message

  .. autofunction:: render_messages


UI Actions
~~~~~~~~~~

  .. autofunction:: uiaction

  .. autofunction:: list_uiactions


Data population
~~~~~~~~~~~~~~~

  .. py:data:: POPULATE_DB_SCHEMA

     Id for database schema creation step. Use it as ``requires`` dependency 
     to make sure that db schema is cerated before execute any other steps.

  .. autoclass:: populate()


Data migration
~~~~~~~~~~~~~~~

  .. autofunction:: register_migration


Events
~~~~~~

Settings events

  .. autofunction:: ptah.events.SettingsInitializing

  .. autofunction:: ptah.events.SettingsInitialized

  .. autofunction:: ptah.events.SettingsGroupModified


Content events

  .. autofunction:: ptah.events.ContentCreatedEvent

  .. autofunction:: ptah.events.ContentAddedEvent

  .. autofunction:: ptah.events.ContentMovedEvent

  .. autofunction:: ptah.events.ContentModifiedEvent

  .. autofunction:: ptah.events.ContentDeletingEvent


Principal events

  .. autofunction:: ptah.events.LoggedInEvent

  .. autofunction:: ptah.events.LoginFailedEvent

  .. autofunction:: ptah.events.LoggedOutEvent

  .. autofunction:: ptah.events.ResetPasswordInitiatedEvent

  .. autofunction:: ptah.events.PrincipalPasswordChangedEvent

  .. autofunction:: ptah.events.PrincipalValidatedEvent

  .. autofunction:: ptah.events.PrincipalAddedEvent

  .. autofunction:: ptah.events.PrincipalRegisteredEvent


Populate db schema

  .. autofunction:: ptah.events.BeforeCreateDbSchema
