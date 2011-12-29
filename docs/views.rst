ptah.library
============

The public api consists of registering static resource directories
and wrapping such resources into a higher level concept, a library.

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
