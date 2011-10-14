Views and Layouts
=================

This is similiar to how Pyramid resolves views but using templates/layouts.
This is independent of Ptah App we just use it as example.  We use Chameleon but this can work with Jinja and Mako.

Conceptual Model
----------------

Let's use Ptah App as an example.  There is a `front-page` content, its
class is ptah_app.content.Page.  The default view for this page is::

    memphis.view.register_view(
        context = Page,
        layout = u'', # empty string means `default layout`
        permission = ptah_cms.View,
        template = memphis.view.template('ptah_app:templates/page.pt'))

So if you render this view::
    >>> from pyramid.requests import Request
    >>> from ptah_cms import Factories    
    >>> import memphis
    >>> root = Factories['root']()
    >>> request = Request.blank('/')
    >>> request.root = root
    >>> request.registry = # put registry
    >>> full_html = memphis.view.render_view('', root['front-page'], request) 
    ... the entire html page with all layout applied

This is ptah_app/templates/page.pt rendered against the page.  This page
does not contain *any* layout.  Then the memphis.view machinery walks up
the layout chain calling each layout with the previous html rendered.

System queries layout for this view::

    >>> snipper = '<div>The result of a view without layout</div>.'
    >>> layout = memphis.view.query_layout(request, root['front-page'], u'')
    >>> layout
    <ptah_app.views.ContentLayout object at ...>
    >>> layout.template
    <PageTemplateFile .. \ptah_app\templates\layoutcontent.pt>
    >>> layout.update() # Since layouts have behavior; you must initialize
    >>> layout.render(snippet)
    .. This will show the layout and substiute ${content} with the snippet.
    >>> layout.(snippet)
    .. this will walk the layout chain and render the full HTML

If we want to walk the layout chain upwards we would see that the ContentLayout's parent essentially is WorkspaceLayout.  Let's take a look
at it by opening ptah_app\views.py and see ContentLayout::

    class ContentLayout(view.Layout):
        """ interface.IContent can be replaced with ptah_cms.Content """
        view.layout('', interfaces.IContent, parent="workspace",
                template=view.template("ptah_app:templates/layoutcontent.pt"))

        def update(self):
            self.actions = listUIActions(self.context, self.request)

You will notice that the parent attribute for the layout is `workspace`.
So the layout engine continues walking up the Layout lineage doing this
same thing::

    snippet = layout.render(snippet)
    p_layout = layout.layout # will be renamed in future
    parent = memphis.view.query_layout(request, root['front-page'], p_layout)
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

Views
-----
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

Comparison with PT/METAL
~~~~~~~~~~~~~~~~~~~~~~~~
TODO - REMEMBER YOU CAN STILL USE NATIVE TEMPLATE COMPOSITION

Comparison with Jinja Inheritance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO - REMEMBER YOU CAN STILL USE NATIVE TEMPLATE COMPOSITION

Comparison with Mako
~~~~~~~~~~~~~~~~~~~~
TODO - REMEMBER YOU CAN STILL USE NATIVE TEMPLATE COMPOSITION

Static Resources
----------------

memphis static resources always are served from /static/ in your URL.  This "static resource prefix" is configurable but the idea is that all static assets are served the same way.  Whether you want it to be /static/ or /assets/ all resources are locatable through this prefix.

since memphis supports this configuration directive for static resources its also possible to introspect them keeping their identity.  it is core behavior to know where a given resource is defined in the code base.

lastly there is additional funcitonality which allows the framework to consolidate all of the static resources into a set of files/folders which can be served from a different server.  e.g.  before production code push you can "re-dump" all static assets and move them to nginx.

Libraries
---------
If you want to include something in the HEAD; libraries are used for this.

Formatters
----------
Convienance functions which provide helpers to display information.  The registered formatters are callable.  They are located in memphis.view.format. An example of this would be for localization, in your settings.ini file you can specify the date format to be displayed.  So if you use the view.format.date_short(datetime.date(2011, 12,12)) the resulting format will be based on the localization settings file.

The goal is to have consistent format for values across a variety of applications, e.g. datetime, timezone, currency.

Messages
--------
This is a reimplementation of pyramid flashmessages.  This could probably be removed.

Snippets
--------
We will either rename this or remove it.  I hate this name.
