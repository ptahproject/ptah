ptah
----

.. automodule:: ptah

Pyramid Config
~~~~~~~~~~~~~~

Imperative-style Pyramid Configuration functions.  These are callable with
a Configurator object, such as::

    config.ptah_init_manage(managers=['*'])

Configurator must be applied before returning WSGI Application.

  .. ptah_init_settings
  
  .. ptah_init_sql
  
  .. ptah_init_manage
  
  .. ptah_init_mailer
  
  .. ptah_init_rest
  
  .. ptah_auth_checker
  
  .. ptah_auth_provider
  
  .. ptah_principal_searcher
  
  .. ptah_uri_resolver
  
  .. ptah_password_changer
  
  .. ptah_layout
  
  .. ptah_snippet
  

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

  .. autoclass:: snippet
     :members: register, pyramid

  .. autofunction:: render_snippet

Layout
~~~~~~

  .. autoclass:: layout
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
    
    System user uri. Permission check always passes for user user. 
    It is possible to use it as effective user::

      >> ptah.auth_service.set_effective_user(ptah.SUPERUSER_URI)
      
    This allow to pass security checks for any user.

  .. autofunction:: auth_checker

  .. autoclass:: auth_provider
     :members: register, pyramid

  .. autofunction:: search_principals

  .. autoclass:: principal_searcher
     :members: register


Password utils
~~~~~~~~~~~~~~

  .. py:data:: pwd_tool

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

Formatter
~~~~~~~~~

  .. autofunction:: format
  
  .. autofunction:: formatter
     
     
Status messages
~~~~~~~~~~~~~~~

  .. autofunction:: add_message

  .. autofunction:: render_messages


UI Actions
~~~~~~~~~~

  .. autofunction:: uiaction

  .. autofunction:: list_uiactions


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
