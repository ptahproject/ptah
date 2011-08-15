""" layout tests """
import os, unittest, tempfile, shutil
from webob.exc import HTTPNotFound
from zope import interface, component
from zope.configuration.config import ConfigurationExecutionError

from memphis import config, view

from memphis.view import meta
from memphis.view.view import View
from memphis.view.layout import Layout, queryLayout

from base import Base

       
class LayoutPagelet(Base):

    def setUp(self):
        Base.setUp(self)
        self.dir = tempfile.mkdtemp()
        
    def tearDown(self):
        Base.tearDown(self)
        shutil.rmtree(self.dir)

    def _setup_memphis(self):
        pass

    def _init_memphis(self, settings={}, handler=None, *args, **kw):
        config.begin()
        config.loadPackage('memphis.view')
        config.addPackage('memphis.view.tests.test_layout')
        if handler is not None:
            handler(*args, **kw)
        config.commit()
        config.initializeSettings(settings, self.p_config)

    def test_layout_register_class_errors(self):
        self.assertRaises(ValueError, view.registerLayout, 'test', klass=None)

        class Layout(object):
            pass
        self.assertRaises(ValueError, view.registerLayout, 'test', klass=Layout)

    def test_layout_register_simple(self):
        view.registerLayout('test')
        self._init_memphis()

        layout = component.getMultiAdapter(
            (View(object(), self.request), 
             object(), self.request), view.ILayout, 'test')

        self.assertEqual(layout.name, 'test')
        self.assertEqual(layout.__name__, 'test')
        self.assertTrue(isinstance(layout, Layout))
        self.assertTrue(issubclass(layout.__class__, Layout))
        self.assertTrue(layout.__class__ is not Layout)

    def test_layout_register_custom_class(self):
        class MyLayout(view.Layout):
            pass

        view.registerLayout('test', klass=MyLayout)
        self._init_memphis()

        layout = component.getMultiAdapter(
            (View(object(), self.request),
             object(), self.request), view.ILayout, 'test')

        self.assertTrue(isinstance(layout, MyLayout))

    def test_layout_register_custom_class_reuse(self):
        # can't reuse same class
        class MyLayout(view.Layout):
            pass

        view.registerLayout('test1', klass=MyLayout)
        view.registerLayout('test2', klass=MyLayout)

        self.assertRaises(
            ConfigurationExecutionError,
            self._init_memphis)

    def test_layout_simple_view(self):
        class View(view.View):
            def render(self):
                return 'View: test'
        class Layout(view.Layout):
            def render(self):
                return '<html>%s</html>'%self.view.render()

        view.registerLayout('test', klass=Layout, view=View)
        self._init_memphis()

        v = View(Context(), self.request)

        # find layout for view
        layout = queryLayout(v, self.request, v.context, 'test')
        self.assertTrue(isinstance(layout, Layout))

        layout.update()
        self.assertEqual(layout.render(),
                         '<html>View: test</html>')

    def test_layout_simple_declarative(self):
        class View(view.View):
            layout = 'test'
            def render(self):
                return 'View: test'
        class Layout(view.Layout):
            view.layout('test', context=Context)
            def render(self):
                return '<html>%s</html>'%self.view.render()

        self._init_memphis(
            {}, meta.LayoutGrokker().grok,  *('Layout', Layout))


        v = View(Context(), self.request)

        layout = queryLayout(v, self.request, v.context, 'test')
        self.assertTrue(isinstance(layout, Layout))

        layout.update()
        self.assertEqual(layout.render(),
                         '<html>View: test</html>')

    def test_layout_simple_notfound(self):
        v = view.View(Context(Context()), self.request)
        layout = queryLayout(v, self.request, v.context, 'test')
        self.assertTrue(layout is None)

    def test_layout_simple_context(self):
        class View(view.View):
            layout = 'test'
            def render(self):
                return 'View: test'
        class Layout(view.Layout):
            def render(self):
                return '<html>%s</html>'%self.view.render()

        view.registerLayout('test', klass=Layout, context=Context)
        self._init_memphis()

        v = View(Context(), self.request)

        # find layout for view
        layout = queryLayout(v, self.request, v.context, 'test')
        self.assertTrue(isinstance(layout, Layout))

        layout.update()
        self.assertEqual(layout.render(),
                         '<html>View: test</html>')

    def test_layout_simple_view_with_template(self):
        class View(view.View):
            layout = 'test'
            def render(self):
                return 'View: test'

        fn = os.path.join(self.dir, 'test.pt')
        tmpl = open(fn, 'wb')
        tmpl.write('<html>${view.render()}</html>')
        tmpl.close()

        view.registerLayout('test', view=View, template = view.template(fn))
        self._init_memphis()

        v = View(Context(), self.request)
        self.assertTrue('<html>View: test</html>' in v().body)

    def test_layout_simple_view_without_template(self):
        class View(view.View):
            layout = 'test'

        view.registerLayout('test', view=View)
        self._init_memphis()

        v = View(Context(), self.request)
        self.assertRaises(RuntimeError, v)

    def test_layout_simple_chain_one_level(self):
        class View(view.View):
            layout = 'test'
            def render(self):
                return 'View: test'

        class LayoutTest(view.Layout):
            def render(self):
                return '<div>%s</div>'%self.view.render()

        class LayoutPage(view.Layout):
            def render(self):
                return '<html>%s</html>'%self.view.render()

        view.registerLayout('', klass=LayoutPage, view=View, parent=None)
        view.registerLayout('test', klass=LayoutTest, view=View, parent='.')
        self._init_memphis()

        v = View(Context(), self.request)
        self.assertTrue('<html><div>View: test</div></html>' in v().body)

    def test_layout_simple_chain_multi_level(self):
        class View(view.View):
            layout = 'test'
            def render(self):
                return 'View: test'

        class LayoutTest(view.Layout):
            def render(self):
                return '<div>%s</div>'%self.view.render()

        class LayoutPage(view.Layout):
            def render(self):
                return '<html>%s</html>'%self.view.render()

        view.registerLayout('', klass=LayoutPage, context=Root, parent=None)
        view.registerLayout('test', klass=LayoutTest, view=View, parent='.')
        self._init_memphis()

        root = Root()
        context = Context(root)

        v = View(context, self.request)
        self.assertTrue('<html><div>View: test</div></html>' in v().body)

        layout = queryLayout(v, self.request, v.context, 'test')
        self.assertTrue(isinstance(layout, LayoutTest))

        rootlayout = queryLayout(v, self.request, v.context, '')
        self.assertTrue(isinstance(rootlayout, LayoutPage))

        rootlayout = queryLayout(v, self.request, root, '')
        self.assertTrue(isinstance(rootlayout, LayoutPage))

        rootlayout = queryLayout(context, self.request, root, '')
        self.assertTrue(isinstance(rootlayout, LayoutPage))


class Context(object):
    
    def __init__(self, parent=None):
        self.__parent__ = parent


class Root(Context):
    pass
