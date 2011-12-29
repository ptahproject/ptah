================
Ptah Walkthrough
================

You should have virtualenv with ptah installed.  Let's create an add-on::

  ~/venv/src$ ../bin/pcreate -t ptah_starter mypkg
  ~/venv/src$ cd mypkg
  ~/venv/src/mypkg$ ../../bin/python setup.py develop

Now lets start the system.  The --reload will start file watcher in paster and will restart the process anytime a .py file is changed::

  ~/venv/src/mypkg$ ../../bin/pserve settings.ini --reload

Goto http://localhost:6543/ and click around.  Things to look out for:

    * There is a simple webpage based on bootstrap css library.

    * On the right hand side there is a tab that says DT and has a pyramid.
      This is the `pyramid_debugtoolbar` which provides all sorts of useful
      feedback during development.

    * There is a button "Goto Ptah Manage UI".  This Management UI has
      a lot of features for you to explore.

What you see on screen when you goto http//localhost:6543/ is a View registered with the / route under the `mypkg` folder in a file, views.py::

    @view_config(renderer='mypkg:templates/homepage.pt', 
                 route_name='home')
                 
    class HomepageView(object):
    
        def __init__(self, request):
            self.request = request
    ..
    
There is no regular expression which matches /, but a name of a route, 'home'.  Let's open up app.py in the same folder to see where `home` route is defined.  If you scan through the main() function you will see::

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

Stepping through code
~~~~~~~~~~~~~~~~~~~~~

    1. create a Pyramid Configurator
    
    2. notify Pyramid you are including other extensions such as ptah

    3. setup RDBMS see settings.ini file for connection string

    4. Initialize ptah settings management with config.ptah_init_settings() which initializes additional ptah.settings and sends ptah.events.SettingsInitializing and ptah.events.SettingsInitialized

    5. config.ptah_init_manage() enables the Ptah Manage Interface and manager=('*',) allows anyone access to it.
       
    6. Setup SQLAlchemy ORM and create tables if necessary.
        
    7. config.add_route('home', '/') registers / to the HomepageView
    
    8. config.add_static_view('_mypkg', 'mypkg:static') allows you to call http://localhost:6543/_mkpkg/app.css which you can see on filesystem, mypkg/static/app.css
    
    9. config.scan() which imports all python modules and performs registration.  You will note there is no `import .views` inside the app.py module.

    10. return config.make_wsgi_app() is Pyramid returning a configured WSGI application.

In summary, you put your application configuration inside of the function which will return a WSGI application.  Any Pyramid extension, such as Ptah is included via config.include('package').  We initialize Ptah.  Then add your application views and routes using Pyramid syntax.  And finally after config.scan() & then enable the Manager Interface.  Lastly return a configured WSGI applicatin.

views.py
~~~~~~~~

Now that we know how the application gets configured and we know how / calls the HomepageView; let's look at how the static resources get included on the homepage.  Let's look at two pieces of code, views.py and homepage.pt.

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

Everytime the view gets created it annotates the request object with its requirements, in this case "bootstrap" and "bootstrap-js".  Subsequenty when Pyramid __calls__ the view, passing the view and the return value to the template 2 additional functions are called `render_includes` and `render_messages` both take the request object. 

render_includes
~~~~~~~~~~~~~~~

You specified what `ptah.library` you needed by using `ptah.include` in the constructor.  Now we need to convert those into HTML for the <head> tag; we call `ptah.render_includes` which will return a HTML string ready to be included into <head>.  `ptah.library` supports depedencies and the render_includes will compute that dependency correct.

render_messages
~~~~~~~~~~~~~~~

User performed actions such as submitting forms, logging in, or providing a user feedback notification is done with messages.  If your application has generated a message you must consume the message by calling `render_messages`.  

Even though we do not display messages in the homepage.pt template we still want to pump any generated messages.  If you have experimented in the Ptah Manage interface and somehow were redirected to Homepage we want the messages pumped.  Else when you go back to template which `rendered_messages` you would see the messages there.

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

There is only two lines of interest::

   ${structure: view.rendered_includes}
   
Which generates the HTML::

    <link type="text/css" rel="stylesheet" href="http://localhost:6543/_ptah/static/bootstrap/bootstrap-1.4.0.min.css" />
    <script src="http://localhost:6543/_ptah/static/jquery/jquery-1.7.min.js"> </script>
    <script src="http://localhost:6543/_ptah/static/bootstrap/js/bootstrap-alerts.js"> </script>
    <script src="http://localhost:6543/_ptah/static/bootstrap/js/bootstrap-buttons.js"> </script>
    <script src="http://localhost:6543/_ptah/static/bootstrap/js/bootstrap-dropdown.js"> </script>
    <script src="http://localhost:6543/_ptah/static/bootstrap/js/bootstrap-modal.js"> </script>
    <script src="http://localhost:6543/_ptah/static/bootstrap/js/bootstrap-popover.js"> </script>
    <script src="http://localhost:6543/_ptah/static/bootstrap/js/bootstrap-scrollspy.js"> </script>
    <script src="http://localhost:6543/_ptah/static/bootstrap/js/bootstrap-tabs.js"> </script>
    <script src="http://localhost:6543/_ptah/static/bootstrap/js/bootstrap-twipsy.js"> </script>

Lastly to reference static assets this line::

    <link rel="shortcut icon"
          href="${request.static_url('mypkg:static/ico/favicon.ico')}" />
          
Generates::

    <link type="text/css" rel="stylesheet" 
          href="http://localhost:6543/_mypkg/app.css" />

Conclusion
~~~~~~~~~~

That demonstrates most of the view functionality.  In the exampeles repository you can look at `ptah_models` for an example of using `ptah.library`.  It ships with a colourpicker widget which requires a javascript library.

More Examples
~~~~~~~~~~~~~

There is a separate `repository for examples <https://github.com/ptahproject/examples>`_.  You can read the `Examples` documentation on-line at 
`http://ptah-examples.readthedocs.org <http://ptah-examples.readthedocs.org/en/latest/index.html>`_.
