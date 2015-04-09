""" layout tests """
import tempfile, shutil, mock
from zope import interface
from pyramid.compat import text_
from pyramid.interfaces import IRequest, IRouteRequest

from ptah.testing import BaseTestCase

class View(object):

    def __init__(self, context=None, request=None):
        self.context = context
        self.request = request

    def __call__(self):
        return {}


class TestLayout(BaseTestCase):

    _includes = ['ptah.renderer']

    def setUp(self):
        BaseTestCase.setUp(self)
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        BaseTestCase.tearDown(self)
        shutil.rmtree(self.dir)

    def test_layout_register_simple(self):
        from ptah.renderer.layout_impl import query_layout

        self.config.add_layout('test')

        layout, context = query_layout(object(), object(), self.request, 'test')

        self.assertEqual(layout.name, 'test')
        self.assertIs(layout.original, None)

    def test_layout_register_custom_class(self):
        from ptah.renderer.layout_impl import query_layout

        class MyLayout(object):
            pass

        self.config.add_layout('test', view=MyLayout)

        layout, context = query_layout(object(), object(), self.request, 'test')
        self.assertIs(layout.original, MyLayout)

    def test_layout_simple_declarative(self):
        from ptah.renderer.layout_impl import LayoutRenderer

        class Layout(View):
            def __call__(self):
                return None

        self.config.add_layout(
            'test', context=Context,
            renderer='ptah.renderer:tests/test-layout-html.pt')

        renderer = LayoutRenderer('test')
        res = renderer('View: test', Context(), self.request)
        self.assertEqual(res.strip(), '<html>View: test</html>')

    def test_layout_pyramid_declarative(self):
        from pyramid.config import Configurator
        from ptah.renderer.layout_impl import ILayout

        config = Configurator(autocommit=True)
        config.include('ptah.renderer')
        config.commit()

        class Layout(View):
            def __call__(self):
                """ """

        config.add_layout('test', view=Layout)

        layout_factory = config.registry.adapters.lookup(
            (interface.providedBy(None),
             IRequest, interface.providedBy(None)), ILayout, name='test')
        self.assertIs(layout_factory.original, Layout)

    def test_layout_simple_notfound(self):
        from ptah.renderer.layout_impl import query_layout

        v = View(Context(Context()), self.request)
        layout, context = query_layout(object(), v.context, self.request,'test')
        self.assertTrue(layout is None)

    def test_layout_simple_chain_multi_level(self):
        from ptah.renderer.layout_impl import LayoutRenderer

        self.config.add_layout(
            'test', parent='.', renderer='ptah.renderer:tests/test-layout.pt')
        self.config.add_layout(
            '', context=Root, parent=None,
            renderer='ptah.renderer:tests/test-layout-html.pt')

        root = Root()
        context = Context(root)
        renderer = LayoutRenderer('test')

        res = renderer('View: test', context, self.request)
        self.assertIn('<html><div>View: test</div>\n</html>', text_(res))

    def test_layout_chain_same_layer_id_on_different_levels(self):
        from ptah.renderer.layout_impl import LayoutRenderer

        self.config.add_layout(
            '', context=Context, parent='.',
            renderer='ptah.renderer:tests/test-layout.pt')
        self.config.add_layout(
            '', context=Root, parent=None,
            renderer='ptah.renderer:tests/test-layout-html.pt')

        root = Root()
        context1 = Context2(root)
        context2 = Context(context1)
        renderer = LayoutRenderer('')

        res = renderer('View: test', context2, self.request)
        self.assertIn('<html><div>View: test</div>\n</html>', text_(res))

    def test_layout_chain_parent_notfound(self):
        self.config.add_layout('', context=Context, parent='page',
                               renderer='ptah.renderer:tests/test-layout.pt')

        root = Root()
        context = Context(root)

        from ptah.renderer.layout_impl import LayoutRenderer
        renderer = LayoutRenderer('')

        res = renderer('View: test', context, self.request)
        self.assertTrue('<div>View: test</div>' in text_(res))

    def test_layout_for_route(self):
        from ptah.renderer.layout_impl import query_layout

        self.config.add_route('test-route', '/test/', use_global_views=False)
        self.config.add_layout(
            'test', route_name='test-route', use_global_views=False)

        layout, context = query_layout(None, Context(), self.request, 'test')
        self.assertIsNone(layout)

        request_iface = self.registry.getUtility(
            IRouteRequest, name='test-route')
        self.request.request_iface = request_iface

        layout = query_layout(None, Context(), self.request, 'test')
        self.assertIsNotNone(layout)

    def test_layout_for_route_global_views(self):
        from ptah.renderer.layout_impl import query_layout

        self.config.add_route('test-route', '/test/', use_global_views=False)
        self.config.add_layout('test', use_global_views=True)

        request_iface = self.registry.getUtility(
            IRouteRequest, name='test-route')
        self.request.request_iface = request_iface

        layout, context = query_layout(object(), object(), self.request, 'test')
        self.assertIsNotNone(layout)

    def test_layout_root(self):
        from ptah.renderer.layout_impl import query_layout

        class Root1(object):
            pass

        class Root2(object):
            pass

        self.config.add_layout('test', root=Root1)

        layout, context = query_layout(Root1(), object(), self.request, 'test')
        self.assertIsNotNone(layout)

        layout, context = query_layout(Root2(), object(), self.request, 'test')
        self.assertIsNone(layout)

    def test_layout_chain_multi_level(self):
        class Layout1(View):
            """ """
        class Layout2(View):
            """ """
        class Layout3(View):
            """ """

        class Context1(object):
            """ """
        class Context2(object):
            """ """
        class Context3(object):
            """ """

        self.config.add_layout(
            'l1', view=Layout1, context=Context1)
        self.config.add_layout(
            'l1', view=Layout2, context=Context2, parent='l1')
        self.config.add_layout(
            'l3', view=Layout3, context=Context3, parent='l1')

        root = Root()
        context1 = Context1()
        context2 = Context2()
        context3 = Context3()

        context1.__parent__ = root
        context2.__parent__ = context1
        context3.__parent__ = context2

        from ptah.renderer.layout_impl import query_layout_chain
        chain = query_layout_chain(root, context1, self.request, 'l1')

        self.assertEqual(len(chain), 1)
        self.assertIs(chain[0][0].original, Layout1)

        chain = query_layout_chain(root, context2, self.request, 'l1')

        self.assertEqual(len(chain), 2)
        self.assertIs(chain[0][0].original, Layout2)
        self.assertIs(chain[1][0].original, Layout1)

        chain = query_layout_chain(root, context3, self.request, 'l3')

        self.assertEqual(len(chain), 3)
        self.assertIs(chain[0][0].original, Layout3)
        self.assertIs(chain[1][0].original, Layout2)
        self.assertIs(chain[2][0].original, Layout1)

    @mock.patch('ptah.renderer.layout_impl.query_layout_chain')
    def test_layout_renderer_no_layouts(self, m):
        from ptah.renderer.layout_impl import LayoutRenderer
        m.return_value = []
        rendr = LayoutRenderer('test')

        o = object()
        res = rendr(o, Context(), self.request)

        self.assertIs(res, o)

    def test_layout_renderer_layout_debug(self):
        from ptah.renderer.layout_impl import LayoutRenderer
        self.config.add_layout('test', view=View,
                               renderer='ptah.renderer:tests/test-layout.pt')
        self.request.__layout_debug__ = True

        rendr = LayoutRenderer('test')
        res = rendr('<h1>text</h1>', Context(), self.request)

        self.assertIn('<!-- layout:', str(res))
        self.assertIn('<h1>text</h1>', str(res))

    @mock.patch('ptah.renderer.layout_impl.random')
    def test_layout_renderer(self, m):
        import ptah.renderer

        m.choice.return_value = 'red'

        self.config.add_layout('test', view=View,
                               renderer='ptah.renderer:tests/test-layout.pt')
        self.config.add_view(
            name='view.html',
            renderer=ptah.renderer.layout('ptah.renderer:tests/dir1/view.pt', 'test'))

        from pyramid.view import render_view_to_response

        res1 = render_view_to_response(Context(), self.request, 'view.html')
        res2 = render_view_to_response(Context(), self.request, 'view.html')
        self.assertEqual(res1.text, res2.text)
        self.assertEqual('<div><h1>Test</h1></div>', res1.text.strip())

    def test_layout_renderer_no_template(self):
        import ptah.renderer
        from pyramid.view import render_view_to_response

        def view(request):
            return 'test'

        self.config.add_view(
            name='view.html', view=view, renderer=ptah.renderer.layout())
        self.config.add_layout(
            '', view=View, renderer='ptah.renderer:tests/test-layout.pt')

        res = render_view_to_response(Context(), self.request, 'view.html')
        self.assertEqual('<div>test</div>', res.text.strip())

    def test_layout_return_response(self):
        import ptah.renderer
        from pyramid.view import render_view_to_response
        from pyramid.httpexceptions import HTTPFound

        def view(request):
            return HTTPFound(location='/')

        self.config.add_view(
            name='view.html', renderer=ptah.renderer.layout())
        self.config.add_layout(
            '', view=view, renderer='ptah.renderer:tests/test-layout.pt')

        res = render_view_to_response(Context(), self.request, 'view.html')
        self.assertIsInstance(res, HTTPFound)

    def test_layout_renderer_layout_info(self):
        from ptah.renderer.layout_impl import query_layout, LayoutRenderer

        self.config.add_layout('test')
        self.config.add_layout('test2', view=View)

        rendr = LayoutRenderer('test')
        l = query_layout(Root(), Context(), self.request, 'test')[0]
        res = rendr.layout_info(l, Context(), self.request, 'content')
        self.assertIn('"layout-factory": "None"', res)
        self.assertIn('content</div>', res)

        rendr = LayoutRenderer('test2')
        l = query_layout(Root(), Context(), self.request, 'test2')[0]
        res = rendr.layout_info(l, Context(), self.request, 'content')
        self.assertIn('"layout-factory": "test_layout.View"', res)

    def test_query_layout_no_request_iface(self):
        from ptah.renderer.layout_impl import query_layout

        self.config.add_layout('test')
        l1 = query_layout(Root(), Context(), self.request, 'test')[0]

        del self.request.request_iface
        l2 = query_layout(Root(), Context(), self.request, 'test')[0]
        self.assertIs(l1, l2)

    @mock.patch('ptah.renderer.layout_impl.query_layout')
    def test_query_layout_chain(self, m):
        from ptah.renderer.layout_impl import query_layout_chain

        m.return_value = (None, None)
        chain = query_layout_chain(Root(), Context(), self.request)

        self.assertEqual([], chain)

    def test_set_layout_data(self):
        request = self.request

        request.set_layout_data(test=123)
        self.assertTrue(hasattr(request, 'layout_data'))
        self.assertIn('test', request.layout_data)
        self.assertEqual(request.layout_data['test'], 123)

    @mock.patch('ptah.renderer.layout_impl.venusian')
    def test_layout_decorator(self, m_venusian):
        from ptah.renderer.layout_impl import layout_config
        from ptah.renderer.layout_impl import ILayout


        @layout_config('test')
        class MyLayout(View):
            def __call__(self):
                return None

        wrp, cb = m_venusian.attach.call_args[0]

        self.assertIs(wrp, MyLayout)

        m_venusian.config.with_package.return_value = self.config
        cb(m_venusian, 'test', MyLayout)

        layout_factory = self.config.registry.adapters.lookup(
            (interface.providedBy(None),
             IRequest, interface.providedBy(None)), ILayout, name='test')
        self.assertIs(layout_factory.original, MyLayout)

        


class Context(object):
    def __init__(self, parent=None, name=''):
        self.__parent__ = parent
        self.__name__ = name


class Context2(object):
    def __init__(self, parent=None):
        self.__parent__ = parent


class Root(Context):
    def __init__(self, name=''):
        self.__name__ = name
