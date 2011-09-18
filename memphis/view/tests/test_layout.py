""" layout tests """
import os, unittest, tempfile, shutil
from webob.exc import HTTPNotFound
from zope import interface, component

from memphis import config, view
from memphis.view.view import View, viewMapper
from memphis.view.layout import Layout, queryLayout
from memphis.view.renderers import Renderer, SimpleRenderer

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
            ValueError,
            self._init_memphis)

    def test_layout_simple_view(self):
        class View(view.View):
            def __call__(self):
                return 'View: test'
        class Layout(view.Layout):
            def render(self, rendered):
                return '<html>%s</html>'%rendered

        view.registerLayout('test', klass=Layout, view=View)
        self._init_memphis()

        v = View(Context(), self.request)

        # find layout for view
        layout = queryLayout(v, self.request, v.context, 'test')
        self.assertTrue(isinstance(layout, Layout))

        layout.update()
        self.assertEqual(layout.render(v()),
                         '<html>View: test</html>')

    def test_layout_simple_declarative(self):
        global Layout

        class View(view.View):
            def __call__(self):
                return 'View: test'
        class Layout(view.Layout):
            view.layout('test', context=Context)
            def render(self, rendered):
                return '<html>%s</html>'%rendered

        self._init_memphis()

        v = View(Context(), self.request)

        layout = queryLayout(v, self.request, v.context, 'test')
        self.assertTrue(isinstance(layout, Layout))

        layout.update()
        self.assertEqual(layout.render(v()),
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

    def test_layout_simple_multilevel(self):
        class View(view.View):
            def __call__(self):
                return 'View: test'
        class Layout(view.Layout):
            def render(self, content):
                return '<html>%s</html>'%content

        view.registerLayout('', klass=Layout, context=Root)
        self._init_memphis()

        root = Root()
        context = Context(root)
        v = View(context, self.request)

        # find layout for view
        layout = queryLayout(v, self.request, context, '')
        self.assertTrue(isinstance(layout, Layout))

        renderer = SimpleRenderer(layout='')
        res = renderer(context, self.request, viewMapper(View))

        self.assertTrue('<html>View: test</html>' in res.body)

    def test_layout_simple_view_with_template(self):
        class View(view.View):
            def __call__(self):
                return 'View: test'

        fn = os.path.join(self.dir, 'test.pt')
        tmpl = open(fn, 'wb')
        tmpl.write('<html>${content}</html>')
        tmpl.close()

        view.registerLayout('test', view=View, template = view.template(fn))
        self._init_memphis()

        renderer = SimpleRenderer(layout='test')

        context = Context()
        res = renderer(context, self.request, viewMapper(View))

        self.assertTrue('<html>View: test</html>' in res.body)

    def test_layout_simple_chain_one_level(self):
        class View(view.View):
            def render(self):
                return 'View: test'

        class LayoutTest(view.Layout):
            def render(self,content):
                return '<div>%s</div>'%content

        class LayoutPage(view.Layout):
            def render(self, content):
                return '<html>%s</html>'%content

        view.registerLayout('', klass=LayoutPage, view=View, parent=None)
        view.registerLayout('test', klass=LayoutTest, view=View, parent='.')
        self._init_memphis()

        context = Context()
        renderer = SimpleRenderer('test')
        res = renderer(context, self.request, viewMapper(View,'render'))

        self.assertTrue('<html><div>View: test</div></html>' in res.body)

    def test_layout_simple_chain_multi_level(self):
        class View(view.View):
            def render(self):
                return 'View: test'

        class LayoutTest(view.Layout):
            def render(self, content):
                return '<div>%s</div>'%content

        class LayoutPage(view.Layout):
            def render(self, content):
                return '<html>%s</html>'%content

        view.registerLayout('', klass=LayoutPage, context=Root, parent=None)
        view.registerLayout('test', klass=LayoutTest, view=View, parent='.')
        self._init_memphis()

        root = Root()
        context = Context(root)
        v = View(context, self.request)

        renderer = SimpleRenderer('test')
        res = renderer(context, self.request, viewMapper(View,'render'))

        self.assertTrue('<html><div>View: test</div></html>' in res.body)

        layout = queryLayout(v, self.request, v.context, 'test')
        self.assertTrue(isinstance(layout, LayoutTest))

        rootlayout = queryLayout(v, self.request, context, '')
        self.assertTrue(isinstance(rootlayout, LayoutPage))

        rootlayout = queryLayout(v, self.request, root, '')
        self.assertTrue(isinstance(rootlayout, LayoutPage))

        rootlayout = queryLayout(context, self.request, root, '')
        self.assertTrue(isinstance(rootlayout, LayoutPage))

    def test_layout_chain_same_layer_id_on_different_levels(self):
        class View(view.View):
            def render(self):
                return 'View: test'

        class Layout1(view.Layout):
            def render(self, content):
                return '<div>%s</div>'%content

        class Layout2(view.Layout):
            def render(self, content):
                return '<html>%s</html>'%content

        view.registerLayout('', klass=Layout1, context=Context, parent='.')
        view.registerLayout('', klass=Layout2, context=Root, parent=None)
        self._init_memphis()

        root = Root()
        context1 = Context2(root)
        context2 = Context(context1)

        renderer = SimpleRenderer()
        res = renderer(context2, self.request, viewMapper(View,'render'))

        self.assertTrue('<html><div>View: test</div></html>' in res.body)

    def test_layout_chain_parent_notfound(self):
        class View(view.View):
            def __call__(self):
                return 'View: test'

        class Layout(view.Layout):
            def render(self, content):
                return '<div>%s</div>'%content

        view.registerLayout('', klass=Layout, context=Context, parent='page')
        self._init_memphis()

        root = Root()
        context = Context(root)

        renderer = SimpleRenderer(layout='')
        res = renderer(context, self.request, viewMapper(View))

        self.assertTrue('<div>View: test</div>' in res.body)

    def test_layout_simple_view_without_template(self):
        class View(view.View):
            def render(self):
                return 'test'

        view.registerLayout('test', view=View)
        self._init_memphis()

        v = View(Context(), self.request)

        layout = queryLayout(v, self.request, v.context, 'test')
        layout.update()
        self.assertTrue('test' == layout.render(v.render()))


class Context(object):

    def __init__(self, parent=None):
        self.__parent__ = parent


class Context2(object):

    def __init__(self, parent=None):
        self.__parent__ = parent


class Root(Context):
    pass
