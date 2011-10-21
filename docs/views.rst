Views and Layouts
=================

This is similiar to how Pyramid resolves views but using templates/layouts.
This is independent of Ptah App we just use it as example.  We use Chameleon but this can work with Jinja and Mako.

Conceptual Model
----------------

Let's use Ptah App as an example.  There is a `front-page` content, its
class is ptah.cmsapp.content.Page.  The default view for this page is::

    ptah.view.register_view(
        context = Page,
        layout = u'', # empty string means `default layout`
        permission = ptah.cms.View,
        template = ptah.view.template('ptah.cmsapp:templates/page.pt'))

NOTE: The layout '' means default.  You can also pass None which means no layout.  If you want
to return a file from a view (you dont need a layout).

So if you render this view::
    >>> from pyramid.requests import Request
    >>> from ptah.cms import Factories    
    >>> import ptah
    >>> root = Factories['root']()
    >>> request = Request.blank('/')
    >>> request.root = root
    >>> request.registry = # put registry
    >>> full_html = ptah.view.render_view('', root['front-page'], request) 
    ... the entire html page with all layout applied

This is ptah.cmsapp/templates/page.pt rendered against the page.  This page
does not contain *any* layout.  Then the ptah.view machinery walks up
the layout chain calling each layout with the previous html rendered.

System queries layout for this view::

    >>> snippet = '<div>The result of a view without layout</div>.'
    >>> layout = ptah.view.query_layout(request, root['front-page'], u'')
    >>> layout
    <ptah.cmsapp.views.ContentLayout object at ...>
    >>> layout.template
    <PageTemplateFile .. \ptah.cmsapp\templates\layoutcontent.pt>
    >>> layout.update() # Since layouts have behavior; you must initialize
    >>> layout.render(snippet)
    .. This will show the layout and substiute ${content} with the snippet.
    >>> layout.(snippet)
    .. this will walk the layout chain and render the full HTML

If we want to walk the layout chain upwards we would see that the ContentLayout's parent essentially is WorkspaceLayout.  Let's take a look
at it by opening ptah.cmsapp\views.py and see ContentLayout::

    class ContentLayout(view.Layout):
        """ interface.IContent can be replaced with ptah.cms.Content """
        view.layout('', interfaces.IContent, parent="workspace",
                template=view.template("ptah.cmsapp:templates/layoutcontent.pt"))

        def update(self):
            self.actions = list_uiactions(self.context, self.request)

You will notice that the parent attribute for the layout is `workspace`.
So the layout engine continues walking up the Layout lineage doing this
same thing::

    snippet = layout.render(snippet)
    p_layout = layout.layout # will be renamed in future
    parent = ptah.view.query_layout(request, root['front-page'], p_layout)
    snippet = parent.render(snippet)
    ...
    continues until there is no parent on a layout.  the top level parent
    will have the <html></html>

Great.  We have reinvented jinja inheritance or METAL.  Not so fast.  It
is true that if you use Pyramid routes and you are not using __parent__ in
your models; the Layout system is of little value.  

Layout's can use Content Heirarchy
----------------------------------

Keep calm and carry on through this section and you will realize why layout
exists.

Presumably in a complex website you have different layouts which depend on
the heirarchy of the website.  For instance, top-level sections will have
a "branded" elements to know you are in the top-level section.  

This is where the layout system comes into play.  Ran out of time. 
Pseudo-code::

  view = pyramid.render_view('/path/to/some/view')
  snippet = templateengine.render(view.__template__(model))
  layout = query_layout(request, model, '')
  while 1:
      snippet = layout.render(snippet)
      layout = query_layout(request, model, layout.parent)
      if layout is None:
          break
  snippet is the full HTML.
  
Let's presume we have the following content model heriarchy::

    / 
    -- section1
      -- page1
    -- section2
      -- page2

Presume we have defined layouts like this::

    PageLayout, this has the <html><body>
      -- WorkspaceLayout, this has <div class="container">
        -- ADiscreteLayout, turtles all the way down

We want to see different HTML in section1 and section2::

    class Section1Layout(view.Layout):
        view.layout('workspace', Section1Model, parent="page")
    
    class Section2Layout(view.Layout):
        view.layout('workspace', Section2Model, parent='page')

Now let's see what happens when we follow layout rendering.  This
happens when rendering page1 and page2::

    page1 model/template gets rendered into snippet.
    layout = query_layout(request, page1, 'workspace') 
    print layout
    <Section1Layout...>
    page2 model/template gets rendered into snippet.
    layout = query_layout(request, page2, 'workspace')
    print layout
    <Section2Layout...>    

Layout API
~~~~~~~~~~
from ptah.view import layout
from ptah.view import Layout
from ptah.view import query_layout
from ptah.view import register_layout

Views
-----
ptah.view.View is the base class for all views.  If you use this as your base class then the
renderer will automatically use layout='' (default layout).  If you use function or do not inherient
from ptah.view.View then the default value for layout = None.

Really no different at all in Pyramid other than configuration statements. There are 2 ways to customize a view.  Override the entire View or you can override the template on a view.

View Templates
~~~~~~~~~~~~~~
An additional feature is that templates which are bound to views can be overridden separately from their views.  You can also list all templates, where it was defined and where it exists on the filesystem.

Template support is currently only Chameleon but its very easy to reimplement this support for Jinja and other template engines.

Layouts
-------
This concept provides ability to nest different HTML generation facilities to create a web page.  You do not have to use Layouts.  You can (and should) use your native template engines macro/inheritance facilities.  You do not have to use/learn Layouts to use Ptah.  Ptah App does use this facility.

Ptah App and Ptah Manage both use Layouts to generate their structure and render full pages.  In reality you will just use a Layout or define your own.  Knowing the ins and outs may not be very interesting to you.  

Layout in Ptah is based on the context in which the template is being rendered.  It is not really a replacement for template composition available inside of the different template implementations.  It is more 

Snippets
--------

An example of Snippet usage can be found in Ptah Manage. If you goto the Introspect module, in the top bar, you see: Introspect, Routes, Events.
If you goto Settings module, in the top bar, you see: Settings.  

You can not use a function to override a snippet.  You can use either a template or a class.  Let's keep it simple and just override the Settings module's snippet.

First let's find the name:
  - Open up Ptah Manage
  - Click on Introspect, then click on ptah
  - Look for `Snippet Types`
  - The name is `ptah-module-actions`
  - If you click on it the hyperlink you will be brought to the definition in source code.  Look for the register_snippet and we see:
  
  view.register_snippet(
    'ptah-module-actions',
    template = view.template('ptah:templates/moduleactions.pt'))

Now lets override the snippet for the Settings module:

  - Unfotunately at this time we dont have introspection on the Ptah Modules.  This is using Pyramid routes/views.  So lets go and look at source:.
  - Open ptah/manage/settings.py
  
  - We see the name of the Module, SettingsModule and registration of it ptah.manageModule('settings')
  
Now lets override the snippet in myapp:
  - Copy the ptah/ptah.cmsapp/templates/moduleactions.pt into myapp/templates/settings-snippet.pt
  - Edit the .pt and add a <li>Modified</li> in the HTML snippet
  - Now open up myapp/views.py and add::

      from ptah import view
      from ptah.manage.settings import SettingsModule
      view.register_snippet(
          'ptah-module-actions',
          context = SettingsModule,
          template = view.template('myapp:templates/settings-snippet.pt'))

Restart and goto ptah-manage and then click on settings.  Look at the
upper left hand side of the screen.

Static Resources
----------------

By using myapp paster template you will see a 'static' folder.  Inside it there is a repoze.gif.  

Looking at myapp/view.py you see::

    view.static('myapp', 'myapp:static')

Let's address it in the URL by going to http://localhost:8080/static/myapp/repoze.gif

You can put anything in there and it will be served and it supports subfolders and assets in those subfolders.  Currently you need to restart the process to see new assets show up but not changes to such assets.  Just the registration.

Changing the `prefix`
~~~~~~~~~~~~~~~~~~~~~

By default the default settings are set for `static`.  If you open up the development.ini you will not see a definition for `static`.  So execute the bin/settings script to see a list of all settings (default and customized).  This is important since there are quite a few defaults and if you had all of these registered in the .ini file it would become unwieldly.

The relevant output from bin/settings::

  * Static resources management

  - static.url: Url (String: static)

  - static.cache_max_age: Cache Max Age (Integer: 0)

If you want to change this edit your .ini file and put static.url=assets then you will be able to see all assets at /assets/myapp/repoze.gif.  Also static.url can be fully qualified. 

Packing static resources
~~~~~~~~~~~~~~~~~~~~~~~~

There is a packing mechanism which will copy all registered static assets into a single directory.  This is very useful during production.
Let's do it::

  $ bin/paster static -d staticassets
  $ ls staticassets
  bootstrap  jquery  myapp  tiny_mce

If you had a custom domain for static assets you can change your production.ini and change static.url=http://media.domain.com/assets/
Your production application when generating urls will use the static.url and you can serve the packed assets efficiently.

Libraries
---------
This name may change.  Main idea is that if your Snippet needs tags inserted into the HEAD you can use the library feature to ensure those HTML supporting assets exist.  An example:

  - The TinyMCE widget is a form field and when it is rendered it does have access to HEAD.
  - In an editor open up ptah/ptah.cmsapp/tinymce.py

Definition of Library::

    # TinyMCE
    view.static(
        'tiny_mce', 'ptah.cmsapp:static/tiny_mce')

    view.library(
        "tiny_mce",
        resource="tiny_mce", # same as view.static name
        path=('tiny_mce.js', 'jquery.tinymce.js'),
        type="js",
        require='jquery')

library parameters:
  identifier, name of the library,
  resource, a static resource registered by view.static() call
  path, list of files to be included in HEAD when library called
  type, whether its JS, CSS, etc.
  require, identifier/name of other library used for dependency resolution

  
So this widget uses another library called jquery.  You can imagine that you will extend TinyMCE with behaviors and inside of your extension you create a library which will require="tiny_mce" which will guarantee that the tinymce assets are available.

Inside of Python if you want to include a library into a request. 

Usage of Library, include::

    from ptah import view
    view.include('tiny_mce', request)

And your request will get all assets for the library.

view.render_includes
~~~~~~~~~~~~~~~~~~~~

If you want to manually render items in head, use render_includes in your
Layout class.

If you want to add dojo, on myapp.layouts.PageLayout add render_includes::

    def render_includes(self):
        includes = super(PageLayout, self).render_includes()
        
        includes += """
        <script src="/static/newapp/dojo/dojo.js" 
        data-dojo-config="isDebug: true,parseOnLoad: true">
        </script>
        """
 
        return includes

Formatters
----------

Convienance functions which provide helpers to display information.  The 
registered formatters are callable.  They are located in ptah.view.format. 
An example of this would be for localization, in your settings.ini file 
you can specify the date format to be displayed.  So if you use the 
view.format.date_short(datetime.date(2011, 12,12)) the resulting format 
will be based on the localization settings file.

The goal is to have consistent format for values across a variety of 
applications, e.g. datetime, timezone, currency.

Messages
--------
This is a reimplementation of pyramid flashmessages.  This will move.

