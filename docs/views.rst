ptah.view
=========

The public api consists of registering static resource directories
and wrapping such resources into a higher level concept, a library.

Static Resources
----------------

By using myapp paster template you will see a 'static' folder.  Inside it there
is a repoze.gif.

Looking at myapp/view.py you see::

    view.static('myapp', 'myapp:static')

Let's address it in the URL by going to http://localhost:8080/static/myapp/repoze.gif

You can put anything in there and it will be served and it supports subfolders
and assets in those subfolders.  Currently you need to restart the process to
see new assets show up but not changes to such assets. Just the registration.

Changing the `prefix`
~~~~~~~~~~~~~~~~~~~~~

By default the default settings are set for `static`.  If you open up the
development.ini you will not see a definition for `static`.  So execute the
bin/settings script to see a list of all settings (default and customized).
This is important since there are quite a few defaults and if you had all of
these registered in the .ini file it would become unwieldly.

The relevant output from bin/settings::

  * Static resources management

  - static.url: Url (String: static)

  - static.cache_max_age: Cache Max Age (Integer: 0)

If you want to change this edit your .ini file and put static.url=assets then
you will be able to see all assets at /assets/myapp/repoze.gif.
Also static.url can be fully qualified.

Packing static resources
~~~~~~~~~~~~~~~~~~~~~~~~

There is a packing mechanism which will copy all registered static assets into
a single directory.  This is very useful during production. Let's do it::

  $ bin/paster static -d staticassets
  $ ls staticassets
  bootstrap  jquery  myapp  tiny_mce

If you had a custom domain for static assets you can change your production.ini
and change static.url=http://media.domain.com/assets/
Your production application when generating urls will use the static.url and you
can serve the packed assets efficiently.

Libraries
---------

Ptah101 has an example of creating a library.  In the example it uses a
3rd party JQuery plugin Colorpicker.

This name may change.  Main idea is that if your Snippet needs tags inserted into
the HEAD you can use the library feature to ensure those HTML supporting assets
exist.  An example::

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


So this widget uses another library called jquery.  You can imagine that you will
extend TinyMCE with behaviors and inside of your extension you create a library
which will require="tiny_mce" which will guarantee that the tinymce assets are
available.

Inside of Python if you want to include a library into a request.

Usage of Library, include::

    from ptah import view
    view.include('tiny_mce', request)

And your request will get all assets for the library.

view.render_includes
~~~~~~~~~~~~~~~~~~~~

TBD

Removed features
~~~~~~~~~~~~~~~~
This section is for historical reasons.  Features which were in ptah.view
but are no longer a part of public API or will be removed:

  * view.pview (view wrapper)
  * view.messages
  * view.snippets
  * view.layout
