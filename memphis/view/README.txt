================
Template layouts
================

Layouts is different way of building skin templates without METAL.

  >>> import os, tempfile, shutil
  >>> import pyramid.testing
  >>> from zope import interface, component
  >>> from memphis import view as api
  >>> from memphis.view import interfaces

  >>> sm = component.getSiteManager()
  >>> request = pyramid.testing.DummyRequest()


Let's define main layout for our skin, it like 'page' macros from basicskin or 
rotterdam. It will contains <html>, <head> and <body> tags::

  >>> temp_dir = tempfile.mkdtemp()
  >>> layoutportal = os.path.join(temp_dir, 'layoutportal.pt')
  >>> open(layoutportal, 'w').write(
  ... '''<html>
  ...   <body>
  ...      <div id="portal" tal:content="structure python:view.render()">
  ...      </div>
  ...   </body>
  ... </html>''')

To use layout you have to register layout::

  >>> class IRoot(interface.Interface):
  ...     """ root object """

  >>> class IItem(interface.Interface):
  ...     """ item """

  >>> class Layout(object):
  ...     pass

  >>> api.registerLayout(
  ...     name = "portal",
  ...     context = IRoot,
  ...     klass = Layout,
  ...     template = api.template(layoutportal, True))

Here is another layout::

  >>> layoutworkspace = os.path.join(temp_dir, 'layoutworkspace.pt')
  >>> open(layoutworkspace, 'w').write('''
  ... <div id="workspace" tal:content="structure python:view.render()"></div>''')

  >>> api.registerLayout(
  ...     name="workspace",
  ...     context=IRoot,
  ...     parent="portal",
  ...     template= api.template(layoutworkspace, True))

Difference is in `parent` parameter, it indicates that 
'workspace' layout uses 'portal' layout as parent. so 'workspace' renderes
 inside 'portal' layout

Now we need pagelet view::

  >>> class IMyView(interface.Interface):
  ...     pass

  >>> class MyView(api.View):
  ...     interface.implements(IMyView)
  ...
  ...     def render(self):
  ...       return self.context.__name__

We can start testing, but we need context::

  >>> class Root(dict):
  ...     interface.implements(IItem, IRoot)
  ...     
  ...     __name__ = 'root'
  ...     __parent__ = None
  ...     
  ...     def __str__(self):
  ...         return "Root"

  >>> root = Root()
  >>> view = MyView(root, request)

It returns context __name__::

  >>> view().body
  'root'

By default `Pagelet` uses layout without name, Let's create one, it will
use `workspace` layout as parent::

  >>> layoutcontent = os.path.join(temp_dir, 'layoutcontent.pt')
  >>> open(layoutcontent, 'w').write('''
  ... <div id="content" tal:content="structure python:view.render()"></div>''')

  >>> api.registerLayout(
  ...     context= IItem,
  ...     parent = "workspace",
  ...     template=api.template(layoutcontent, True))

  >>> print view().body
  <html>
     <body>
        <div id="portal"><div id="workspace"><div id="content">root</div></div></div>
     </body>
  </html>

Use 'queryLayout' to get layout for view::

  >>> from memphis.view.layout import queryLayout

  >>> layoutOb = queryLayout(view, request, view.context, name='workspace')
  >>> layoutOb
  <memphis.view.layout.Layout<workspace> object at ...>

  >>> print layoutOb()
  <html>
    <body>
       <div id="portal"><div id="workspace">root</div></div>
    </body>
  </html>

Exceptions

  >>> layoutOb.template = None
  >>> layoutOb()
  Traceback (most recent call last):
  ...
  RuntimeError: Can't render layout: workspace

  >>> layoutOb.layout = 'unknown'
  >>> layoutOb()
  Traceback (most recent call last):
  ...
  LayoutNotFound: unknown


All three layouts are rendered. View is rendered inside default (nameless)
layout then in -> 'workspace' layout -> 'portal' layout.

Let's create more content objects::

  >>> class IFolder(IItem):
  ...     pass

  >>> class Folder(dict):
  ...     interface.implements(IFolder)
  ...     def __init__(self, name, parent):
  ...         self.__name__ = name
  ...         self.__parent__ = parent

  >>> folder1 = Folder('folder1', root)
  >>> root['folder1'] = folder1

  >>> print MyView(folder1, request)().body
  <html>
    <body>
      <div id="portal"><div id="workspace"><div id="content">folder1</div></div></div>
    </body>
  </html>


And some more objects::

  >>> folder1_1 = Folder('folder1_1', folder1)
  >>> root['folder1']['folder1_1'] = folder1_1

  >>> folder1_1_1 = Folder('folder1_1_1', folder1_1)
  >>> root['folder1']['folder1_1']['folder1_1_1'] = folder1_1_1

  >>> print MyView(folder1_1_1, request)().body
  <html>
    <body>
      <div id="portal"><div id="workspace"><div id="content">folder1_1_1</div></div></div>
    </body>
  </html>


Let's use more complex example. For example other developer decides to
change how portal looks for folder1 object. they want that all folder1
and all it's childs(folder1_1, folder1_1_1) have same look.

Let's add '<table>' with couple columns

  >>> layoutcolumns = os.path.join(temp_dir, 'layoutcolumns.pt')
  >>> open(layoutcolumns, 'w').write('''
  ... <table id="columns">
  ...   <tr>
  ...     <td id="column1">Column1</td>
  ...       <td id="column2" tal:content="structure python:view.render()"></td>
  ...     <td id="column3">Column3</td>
  ...   </tr>
  ... </table>''')


Register layout::

  >>> class IFolder1(interface.Interface):
  ...     pass

  >>> api.registerLayout(
  ...     name="workspace",
  ...     context=IFolder1,
  ...     parent="portal",
  ...     template=api.template(layoutcolumns, True))

  >>> interface.directlyProvides(folder1, IFolder1)

  >>> print MyView(folder1, request)().body
  <html>
    <body>
      <div id="portal"><table id="columns">
          <tr>
            <td id="column1">Column1</td>
            <td id="column2"><div id="content">folder1</div></td>
            <td id="column3">Column3</td>
          </tr>
        </table></div>
    </body>
  </html>

folder1 uses new 'workspace' layout, but what about subfolders folders::

  >>> print MyView(folder1_1, request)().body
  <html>
    <body>
      <div id="portal"><table id="columns">
          <tr>
            <td id="column1">Column1</td>
            <td id="column2"><div id="content">folder1_1</div></td>
            <td id="column3">Column3</td>
          </tr> 
        </table></div>
    </body>
  </html>


  >>> print MyView(folder1_1_1, request)().body
  <html>
    <body>
      <div id="portal"><table id="columns">
          <tr>
            <td id="column1">Column1</td>
            <td id="column2"><div id="content">folder1_1_1</div></td>
            <td id="column3">Column3</td>
          </tr>
        </table></div>
    </body>
  </html>


Let's change how folder1_1 looks, to do this we can replace nameless layout.
Remark: we can use nameless layout as parent with `parent="."`::

  >>> layoutcontent1_1 = os.path.join(temp_dir, 'layoutcontent1_1.pt')
  >>> open(layoutcontent1_1, 'w').write('''
  ... <div id="content1_1">
  ...   <h1>Folder1_1</h1>
  ...   <div tal:content="structure python:view.render()"></div>
  ... </div>''')

  >>> class IFolder1_1(interface.Interface):
  ...     pass

  >>> api.registerLayout(
  ...     context=IFolder1_1,
  ...     parent=".",
  ...     template=api.template(layoutcontent1_1, True))

  >>> interface.directlyProvides(folder1_1, IFolder1_1)
  
  >>> print MyView(folder1_1, request)().body
  <html>
    <body>
      <div id="portal"><table id="columns">
          <tr>
            <td id="column1">Column1</td>
            <td id="column2"><div id="content"><div id="content1_1">
               <h1>Folder1_1</h1>
               <div>folder1_1</div>
            </div></div></td>
            <td id="column3">Column3</td>
          </tr>
        </table></div>
     </body>
  </html>

It still uses nameless layout that we defined for 'root'. 

And same for folder1_1_1

  >>> layoutcontent1_1_1 = os.path.join(temp_dir, 'layoutcontent1_1_1.pt')
  >>> open(layoutcontent1_1_1, 'w').write('''
  ... <div id="content1_1_1">
  ...   <h1>Folder1_1_1</h1>
  ...   <div>${view.render()}</div>
  ... </div>''')

  >>> class IFolder1_1_1(interface.Interface):
  ...     pass

  >>> api.registerLayout(
  ...     context=IFolder1_1_1,
  ...     parent=".",
  ...     template=api.template(layoutcontent1_1_1, True))

  >>> interface.directlyProvides(folder1_1_1, IFolder1_1_1)

  >>> print MyView(folder1_1_1, request)().body
  <html>
    <body>
      <div id="portal"><table id="columns">
         <tr>
            <td id="column1">Column1</td>
            <td id="column2"><div id="content"><div id="content1_1">
              <h1>Folder1_1</h1>
              <div><div id="content1_1_1">
                 <h1>Folder1_1_1</h1>
                 <div>folder1_1_1</div>
              </div></div>
            </div></div></td>
            <td id="column3">Column3</td>
         </tr>
      </table></div>
    </body>
  </html>

  >>> shutil.rmtree(temp_dir)
