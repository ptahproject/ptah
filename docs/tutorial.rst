================
Ptah Walkthrough
================

You should have a virtualenv with ptah installed.  Let's create an add-on::

  ~/venv/src$ ../bin/pcreate -t ptah_starter mypkg
  ~/venv/src$ cd mypkg
  ~/venv/src/mypkg$ ../../bin/python setup.py develop

Now let's start the system.  --reload will start the file watcher in paster and will restart the process any time a .py file is changed::

  ~/venv/src/mypkg$ ../../bin/pserve settings.ini --reload

Go to http://localhost:6543/ and click around.  Things to look out for:

    * There is a simple webpage based on the bootstrap CSS library.

    * On the right hand side there is a tab that says DT and has a pyramid.
      This is the `pyramid_debugtoolbar` which provides all sorts of useful
      feedback during development.

    * There is a button "Goto Ptah Manage UI".  This Management UI has
      a lot of features for you to explore.

What you see on screen when you go to http://localhost:6543/ is a View registered with the / route under the `mypkg` folder in a file, views.py::

    @view_config(renderer='mypkg:templates/homepage.pt',
                 route_name='home')

    class HomepageView(object):

        def __init__(self, request):
            self.request = request
    ..

There is no regular expression which matches /, but a name of a route, 'home'.  Let's open up app.py in the same folder to see where the `home` route is defined.  If you scan through the main() function you will see::

    config.add_route('home', '/')

That is it.  Let's take this opportunity to review the main() function.  All comments have been removed::

    def main(global_config, **settings):

        config = Configurator(settings=settings,
                              session_factory = session_factory,
                              authentication_policy = auth_policy)
        config.include('ptah')

        config.ptah_init_sql()

        config.ptah_init_settings()

        config.ptah_init_manage(managers=('*',))

        Base = ptah.get_base()
        Base.metadata.create_all()

        config.add_route('home', '/')
        config.add_static_view('_mypkg', 'mypkg:static')
        config.scan()

        return config.make_wsgi_app()

Stepping through the code
~~~~~~~~~~~~~~~~~~~~~~~~~

    1. Instantiate a Pyramid Configurator.

    2. Notify Pyramid to run the 'ptah' extension.

    3. Set up the RDBMS. (See the "settings.ini" file for the connection string.)

    4. Activate ptah settings management with config.ptah_init_settings() which initializes additional ptah.settings and sends ptah.events.SettingsInitializing and ptah.events.SettingsInitialized.

    5. `config.ptah_init_manage()` enables the Ptah Manage Interface and `manager=('*',)` allows anyone access to it.

    6. Set up the SQLAlchemy ORM and create tables if necessary.

    7. `config.add_route('home', '/')` registers / to the HomepageView

    8. `config.add_static_view('_mypkg', 'mypkg:static')` allows you to call http://localhost:6543/_mkpkg/app.css which you can see on filesystem, mypkg/static/app.css

    9. config.scan() imports all python modules in your application and performs registration. You will note there is no `import .views` inside the app.py module, because the scan makes that unnecessary.

    10. `return config.make_wsgi_app()` is Pyramid returning a configured WSGI application.

In summary, you put your application configuration inside of the function which will return a WSGI application.  Any Pyramid extension, such as Ptah, is included via config.include('package_name').  We initialize Ptah.  Then add your application views and routes using Pyramid syntax. We run a scan and then enable the Manager Interface. Lastly, return the configured WSGI application.

views.py
~~~~~~~~

Now that we know how the application gets configured and we know how / calls the HomepageView, let's look at how the static resources get included on the homepage.  We will examine views.py and the template homepage.pt.

Let's look at views.py::

    import ptah

    class HomepageView(object):

        def __init__(self, request):
            self.request = request
            ptah.include(request, 'bootstrap')
            ptah.include(request, 'bootstrap-js')

        def __call__(self):
            request = self.request
            self.rendered_includes = ptah.render_includes(request)
            self.rendered_messages = ptah.render_messages(request)
            return {}

Every time the view gets created it annotates the request object with its requirements, in this case "bootstrap" and "bootstrap-js".  Subsequenty, when Pyramid __calls__ the view, passing the view and the return value to the template, 2 additional functions are called: `render_includes` and `render_messages`. Both take the request object as a parameter.

render_includes
~~~~~~~~~~~~~~~

You specified what `ptah.library` you needed by using `ptah.include` in the constructor.  Now we need to convert those into HTML for the <head> tag; we call `ptah.render_includes` which will return an HTML string ready to be included in the <head>.  `ptah.library` supports dependencies and render_includes() will compute that dependency correctly.

render_messages
~~~~~~~~~~~~~~~

User performed actions such as submitting forms, logging in, or providing a user feedback notification is done with messages.  These have been called "flash messages" in other web frameworks.  Any messages your application has generated must be consumed (i.e. rendered) by calling `render_messages()`.

Even though we do not create messages in the homepage.pt template, we still want to pump any previously generated messages.  For instance, you might experiment with the Ptah Manage interface and somehow be redirected to the Homepage -- you would want to see any messages created in previous requests immediately. This is why messages are usually handled in master (layout) templates.

homepage.pt
~~~~~~~~~~~

Now let's go and look at the template which renders the HTML.  It can be found in `mkpkg/templates/homepage.pt` and there are only a few lines of interest in the <head>::

  <head>
    <meta charset="utf-8">
    <title>mypkg, made with Ptah!</title>
    ${structure: view.rendered_includes}
    <link type="text/css" rel="stylesheet"
          href="${request.static_url('empty:static/app.css')}" />
    <link rel="shortcut icon"
          href="${request.static_url('empty:static/ico/favicon.ico')}" />
  </head>

This line::

   ${structure: view.rendered_includes}

...generates the HTML::

    <link type="text/css" rel="stylesheet" href="http://localhost:6543/_ptah/static/bootstrap/bootstrap-1.4.0.min.css" />
    <script src="http://localhost:6543/_ptah/static/jquery/jquery-1.7.min.js"> </script>
    <script src="http://localhost:6543/_ptah/static/bootstrap/bootstrap-2.0.1.min.js"> </script>

Lastly to reference static assets this line::

    <link rel="shortcut icon"
          href="${request.static_url('mypkg:static/ico/favicon.ico')}" />

...generates::

    <link type="text/css" rel="stylesheet"
          href="http://localhost:6543/_mypkg/app.css" />

Conclusion
~~~~~~~~~~

This demonstrates most of the view functionality.  In the examples repository you can look at `ptah_models` for an example of using `ptah.library`.  It ships with a colourpicker widget which requires a javascript library.

More Examples
~~~~~~~~~~~~~

There is a separate `repository for examples <https://github.com/ptahproject/examples>`_.  You can read the `Examples` documentation on-line at
`http://ptah-examples.readthedocs.org <http://ptah-examples.readthedocs.org/en/latest/index.html>`_.
