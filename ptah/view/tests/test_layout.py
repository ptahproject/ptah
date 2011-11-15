""" layout tests """
import os, tempfile, shutil
from zope import interface
from pyramid.interfaces import IRouteRequest

from ptah import view
from ptah.view.interfaces import ILayout
from ptah.view.layout import Layout, LayoutRenderer, \
    query_layout, query_layout_chain

from base import Base


class TestLayout(Base):

    def setUp(self):
        Base.setUp(self)
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        Base.tearDown(self)
        shutil.rmtree(self.dir)

    def _setup_ptah(self):
        pass

    def test_layout_register_class_errors(self):
        self.assertRaises(ValueError, view.register_layout, 'test',klass=None)

        class LayoutCls(object):
            pass
        self.assertRaises(ValueError, view.register_layout, 'test',klass=LayoutCls)

    def test_layout_register_simple(self):
        view.register_layout('test')
        self._init_ptah()

        layout = self.registry.getMultiAdapter(
            (object(), self.request), ILayout, 'test')

        self.assertEqual(layout.name, 'test')
        self.assertEqual(layout.__name__, 'test')
        self.assertTrue(isinstance(layout, Layout))
        self.assertTrue(issubclass(layout.__class__, Layout))
        self.assertTrue(layout.__class__ is not Layout)

    def test_layout_register_custom_class(self):
        class MyLayout(view.Layout):
            pass

        view.register_layout('test', klass=MyLayout)
        self._init_ptah()

        layout = self.registry.getMultiAdapter(
            (object(), self.request), ILayout, 'test')

        self.assertTrue(isinstance(layout, MyLayout))

    def test_layout_simple_view(self):
        class View(view.View):
            def __call__(self):
                return 'View: test'
        class Layout(view.Layout):
            def render(self, rendered):
                return '<html>%s</html>'%rendered

        view.register_layout('test', klass=Layout)
        self._init_ptah()

        v = View(Context(), self.request)

        # find layout for view
        layout = query_layout(v.context, self.request, 'test')
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

        self._init_ptah()

        v = View(Context(), self.request)

        layout = query_layout(v.context, self.request, 'test')
        self.assertTrue(isinstance(layout, Layout))

        layout.update()
        self.assertEqual(layout.render(v()),
                         '<html>View: test</html>')

    def test_layout_simple_notfound(self):
        v = view.View(Context(Context()), self.request)
        layout = query_layout(v.context, self.request, 'test')
        self.assertTrue(layout is None)

    def test_layout_simple_context(self):
        class View(view.View):
            layout = 'test'
            def render(self):
                return 'View: test'
        class Layout(view.Layout):
            def render(self, content):
                return '<html>%s</html>'%content

        view.register_layout('test', klass=Layout, context=Context)
        self._init_ptah()

        v = View(Context(), self.request)

        # find layout for view
        layout = query_layout(v.context, self.request, 'test')
        self.assertTrue(isinstance(layout, Layout))

        layout.update()
        self.assertEqual(layout.render(v.render()), '<html>View: test</html>')

    def test_layout_simple_multilevel(self):
        class Layout(view.Layout):
            def render(self, content):
                return '<html>%s</html>'%content

        view.register_layout('', klass=Layout, context=Root)
        self._init_ptah()

        root = Root()
        context = Context(root)

        # find layout for view
        layout = query_layout(context, self.request, '')
        self.assertTrue(isinstance(layout, Layout))

        renderer = LayoutRenderer('')
        res = renderer(context, self.request, 'View: test')

        self.assertTrue('<html>View: test</html>' in res)

    def test_layout_simple_view_with_template(self):
        fn = os.path.join(self.dir, 'test.pt')
        tmpl = open(fn, 'wb')
        tmpl.write('<html>${content}</html>')
        tmpl.close()

        view.register_layout('test', template = view.template(fn))
        self._init_ptah()

        renderer = LayoutRenderer('test')

        context = Context()
        res = renderer(context, self.request, 'View: test')

        self.assertTrue('<html>View: test</html>' in res)

    def test_layout_simple_chain_one_level(self):
        class LayoutTest(view.Layout):
            def render(self,content):
                return '<div>%s</div>'%content

        class LayoutPage(view.Layout):
            def render(self, content):
                return '<html>%s</html>'%content

        view.register_layout('', klass=LayoutPage, parent=None)
        view.register_layout('test', klass=LayoutTest, parent='.')
        self._init_ptah()

        context = Context()
        renderer = LayoutRenderer('test')
        res = renderer(context, self.request, 'View: test')

        self.assertTrue('<html><div>View: test</div></html>' in res)

    def test_layout_simple_chain_multi_level(self):
        class LayoutTest(view.Layout):
            def render(self, content):
                return '<div>%s</div>'%content

        class LayoutPage(view.Layout):
            def render(self, content):
                return '<html>%s</html>'%content

        view.register_layout('', klass=LayoutPage, context=Root, parent=None)
        view.register_layout('test', klass=LayoutTest, parent='.')
        self._init_ptah()

        root = Root()
        context = Context(root)

        renderer = LayoutRenderer('test')
        res = renderer(context, self.request, 'View: test')

        self.assertTrue('<html><div>View: test</div></html>' in res)

        layout = query_layout(context, self.request, 'test')
        self.assertTrue(isinstance(layout, LayoutTest))

        rootlayout = query_layout(context, self.request, '')
        self.assertTrue(isinstance(rootlayout, LayoutPage))

        rootlayout = query_layout(root, self.request, '')
        self.assertTrue(isinstance(rootlayout, LayoutPage))

    def test_layout_chain_same_layer_id_on_different_levels(self):
        class Layout1(view.Layout):
            def render(self, content):
                return '<div>%s</div>'%content

        class Layout2(view.Layout):
            def render(self, content):
                return '<html>%s</html>'%content

        view.register_layout('', klass=Layout1, context=Context, parent='.')
        view.register_layout('', klass=Layout2, context=Root, parent=None)
        self._init_ptah()

        root = Root()
        context1 = Context2(root)
        context2 = Context(context1)

        renderer = LayoutRenderer('')
        res = renderer(context2, self.request, 'View: test')

        self.assertTrue('<html><div>View: test</div></html>' in res)

    def test_layout_chain_parent_notfound(self):
        class Layout(view.Layout):
            def render(self, content):
                return '<div>%s</div>'%content

        view.register_layout('', klass=Layout, context=Context, parent='page')
        self._init_ptah()

        root = Root()
        context = Context(root)

        renderer = LayoutRenderer('')
        res = renderer(context, self.request, 'View: test')

        self.assertTrue('<div>View: test</div>' in res)

    def test_layout_simple_view_without_template(self):
        class View(view.View):
            def render(self):
                return 'test'

        view.register_layout('test')
        self._init_ptah()

        v = View(Context(), self.request)

        layout = query_layout(v.context, self.request, 'test')
        layout.update()
        self.assertTrue('test' == layout.render(v.render()))

    def test_layout_for_route(self):
        view.register_route('test-route', '/test/', use_global_views=True)
        view.register_layout('test', route = 'test-route')
        self._init_ptah()

        layout = query_layout(Context(), self.request, 'test')
        self.assertIsNone(layout)

        request_iface = self.registry.getUtility(
            IRouteRequest, name='test-route')
        interface.directlyProvides(self.request, request_iface)

        layout = query_layout(Context(), self.request, 'test')
        self.assertIsNotNone(layout)

    def test_layout_chain_multi_level(self):
        class Layout1(view.Layout):
            """ """
        class Layout2(view.Layout):
            """ """
        class Layout3(view.Layout):
            """ """

        class Context1(object):
            """ """
        class Context2(object):
            """ """
        class Context3(object):
            """ """

        view.register_layout('l1', klass=Layout1, context=Context1)
        view.register_layout('l1', klass=Layout2, context=Context2, parent='l1')
        view.register_layout('l3', klass=Layout3, context=Context3, parent='l1')
        self._init_ptah()

        root = Root()
        context1 = Context1()
        context2 = Context2()
        context3 = Context3()

        context1.__parent__ = root
        context2.__parent__ = context1
        context3.__parent__ = context2

        chain = query_layout_chain(context1, self.request, 'l1')

        self.assertEqual(len(chain), 1)
        self.assertIsInstance(chain[0], Layout1)

        chain = query_layout_chain(context2, self.request, 'l1')

        self.assertEqual(len(chain), 2)
        self.assertIsInstance(chain[0], Layout2)
        self.assertIsInstance(chain[1], Layout1)

        chain = query_layout_chain(context3, self.request, 'l3')

        self.assertEqual(len(chain), 3)
        self.assertIsInstance(chain[0], Layout3)
        self.assertIsInstance(chain[1], Layout2)
        self.assertIsInstance(chain[2], Layout1)


class Context(object):

    def __init__(self, parent=None):
        self.__parent__ = parent


class Context2(object):

    def __init__(self, parent=None):
        self.__parent__ = parent


class Root(Context):
    pass
