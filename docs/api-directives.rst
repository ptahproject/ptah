Pyramid Directives
------------------

Pyramid Configuration directive from Ptah.  An example:

  .. code-block:: python

    auth_policy = AuthTktAuthenticationPolicy('secret')
    session_factory = UnencryptedCookieSessionFactoryConfig('secret')

    def main(global_config, **settings):
        """ This is your application startup."""

        config = Configurator(settings=settings,
                              session_factory = session_factory,
                              authentication_policy = auth_policy)
        config.include('ptah')

        config.ptah_init_settings()
        config.ptah_init_sql()


.. function:: ptah_init_sql(prefix='sqlalchemy.')

    This directive creates new SQLAlchemy engine and bind session and 
    declarative base.

    :param prefix: INI settings prefix, default is ``sqlalchemy.``

    Example::

      [app:ptah]
      sqlalchemy.url = sqlite:///%(here)s/var/db.sqlite


.. function:: ptah_init_settings(settings=None)

    Initialize settings management system and load settings from system
    settings. Also it sends :py:class:`ptah.events.SettingsInitializing`
    and then :py:class:`ptah.events.SettingsInitialized`. By default
    it reads info from ``config.registry.settings``. Its possible to pass
    custom settings as first parameter.

    :param settings: Custom settings

    .. code-block:: python

      config = Configurator()
      config.include('ptah')

      # initialize ptah setting management system
      config.ptah_initialize_settings()
      ..
      config.ptah_initialize_settings({'ptah.managers': '["*"]'})


.. function:: ptah_init_manage

   Initialize and enable ptah management subsystem.

   :param name: Management ui prefix. Default is ``ptah-manage``.
   :param access_manager: Set custom access manager.
   :param managers: List of user logins with access rights to 
       `ptah management ui`.
   :param manager_role: Specific role with access rights to ptah management ui.
   :param disable_modules: List of modules names to hide in manage ui

   Also it possible to enable and configure management subsystem with
   settings in ini file::

     [app:ptah]

     ptah.manage = "ptah-manage"
     ptah.managers = ["*"]
     ptah.manager_role = ...
     ptah.disable_modules = ...     


.. function:: ptah_init_mailer(mailer)

   Set mailer object. Mailer interface is compatible with ``repoze.sendmail``
   and ``pyramid_mailer``. By default stub mailer is beeing used.

   :param mailer: Mailer object


.. function:: ptah_init_rest

   Eanble ptah rest api. It registers two routes::

     /__rest__/login

     and

     /__rest__/{service}/*subpath


.. function:: ptah_auth_checker(checker)

   Register auth checker. 
   Checker function interface :py:class:`ptah.interfaces.auth_checker`

   :param checker: Checker function

   .. code-block:: python

      config = Configurator()
      config.include('ptah')

      def my_checker(info):
          ...

      config.ptah_auth_checker(my_checker)


.. function:: ptah_auth_provider(name, provider)

   Register auth provider. Authentication provider 
   interface :py:class:`ptah.interfaces.AuthProvider`

  
.. function:: ptah_principal_searcher(name, searcher)

   Register principal searcher function.
   Principal searcher function interface 
   :py:func:`ptah.interfaces.principal_searcher`

  
.. function:: ptah_uri_resolver(schema, resolver)

   Register resolver for given schema. 
   Resolver function interface :py:func:`ptah.interfaces.resolver`


   :param schema: uri schema
   :param resolver: Callable object that accept one parameter.

   .. code-block:: python

       config = Configurator()
       config.include('ptah')
          
       def my_resolver(uri):
           ....

       config.ptah_uri_resolver('custom-schema', my_resolver)


.. function:: ptah_password_changer(schema, changer)

   Register password changer function for specific user uri schema.
   Password changer interface :py:func:`ptah.intefaces.password_changer`

   :param schema: Principal uri schema.
   :param changer: Function 

   .. code-block:: python

       config = Configurator()
       config.include('ptah')
          
       config.ptah_password_changer('custom-schema', custom_changer)


.. function:: ptah_layout

    Registers a layout.

    :param name: Layout name
    :param context: Specific context for this layout.
    :param root:  Root object
    :param parent: A parent layout. None means no parent layout.
    :param renderer: A pyramid renderer
    :param route_name: A pyramid route_name. Apply layout only for
        specific route
    :param use_global_views: Apply layout to all routes. even is route
        doesnt use use_global_views.
    :param view: Layout implementation (same as for pyramid view)

    .. code-block:: python

      config = Configurator()
      config.include('ptah')

      config.ptah_layout(
          'page', parent='page', 
          renderer='ptah:template/page.pt')

      config.add_view('
          index.html',
          wrapper=ptah.wrap_layout(),
          renderer = '...')

  
.. function:: ptah_snippet
    
    Register snippet. Snippet is very similar to pyramid view.
    It doesnt availble with pyramid traversing. It doesnt have
    security.

    :param name: Snippet name
    :param context: Snippet context
    :param view: View implementation
    :param renderer: Pyramid renderer

    .. code-block:: python

       config = Configurator()
       config.include('ptah')

       config.ptah_snippet('test', view=snippet, renderer='.../test.pt')
