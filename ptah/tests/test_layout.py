""" layout tests """
import os, tempfile, shutil
from zope import interface
from pyramid.compat import bytes_, text_
from pyramid.interfaces import IRequest
from pyramid.interfaces import IRouteRequest

import ptah
from ptah.testing import PtahTestCase


class TestLayout(PtahTestCase):

    _init_ptah = False

    def setUp(self):
        PtahTestCase.setUp(self)
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        PtahTestCase.tearDown(self)
        shutil.rmtree(self.dir)

    def test_layout_register_simple(self):
        from ptah.layout import query_layout
        ptah.layout.register('test')
        self.init_ptah()

        layout, context = query_layout(object(), object(), self.request, 'test')

        self.assertEqual(layout.name, 'test')
        self.assertIs(layout.original, ptah.View)

    def test_layout_register_custom_class(self):
        from ptah.layout import query_layout
        class MyLayout(ptah.View):
            pass

        ptah.layout.register('test', view=MyLayout)
        self.init_ptah()

        layout, context = query_layout(object(), object(), self.request, 'test')
        self.assertIs(layout.original, MyLayout)

    def test_layout_simple_declarative(self):
        from ptah.layout import LayoutRenderer

        @ptah.layout('test', context=Context,
                     renderer='ptah:tests/test-layout-html.pt')
        class Layout(ptah.View):
            def __call__(self):
                return None

        self.init_ptah()

        renderer = LayoutRenderer('test')
        self.request.wrapped_body = 'View: test'
        self.request.wrapped_response = self.request.response

        res = renderer(Context(), self.request).text
        self.assertEqual(res.strip(), '<html>View: test</html>')

    def test_layout_pyramid_declarative(self):
        from ptah.layout import ILayout
        from pyramid.config import Configurator

        config = Configurator(autocommit=True)
        config.include('ptah')
        self.init_ptah()

        class Layout(ptah.View):
            def __call__(self):
                """ """

        config.ptah_layout('test', view=Layout)

        layout_factory = config.registry.adapters.lookup(
            (interface.providedBy(None),
             IRequest, interface.providedBy(None)), ILayout, name='test')
        self.assertIs(layout_factory.original, Layout)

    def test_layout_simple_notfound(self):
        from ptah.layout import query_layout

        v = ptah.View(Context(Context()), self.request)
        layout, context = query_layout(object(), v.context, self.request,'test')
        self.assertTrue(layout is None)

    def test_layout_simple_chain_multi_level(self):
        from ptah.layout import query_layout, LayoutRenderer
        ptah.layout.register('test', parent='.',
                             renderer='ptah:tests/test-layout.pt')
        ptah.layout.register('', context=Root, parent=None,
                             renderer='ptah:tests/test-layout-html.pt')
        self.init_ptah()

        root = Root()
        context = Context(root)

        renderer = LayoutRenderer('test')
        self.request.wrapped_body = 'View: test'
        self.request.wrapped_response = self.request.response

        res = renderer(context, self.request).text
        self.assertTrue('<html><div>View: test</div>\n</html>' in text_(res))

    def test_layout_chain_same_layer_id_on_different_levels(self):
        from ptah.layout import LayoutRenderer
        ptah.layout.register('', context=Context, parent='.',
                             renderer='ptah:tests/test-layout.pt')
        ptah.layout.register('', context=Root, parent=None,
                             renderer='ptah:tests/test-layout-html.pt')
        self.init_ptah()

        root = Root()
        context1 = Context2(root)
        context2 = Context(context1)

        renderer = LayoutRenderer('')
        self.request.wrapped_body = 'View: test'
        self.request.wrapped_response = self.request.response

        res = renderer(context2, self.request).body
        self.assertEqual('<html><div>View: test</div>\n</html>\n', text_(res))

    def test_layout_chain_parent_notfound(self):
        ptah.layout.register('', context=Context, parent='page',
                             renderer='ptah:tests/test-layout.pt')
        self.init_ptah()

        root = Root()
        context = Context(root)

        from ptah.layout import LayoutRenderer
        renderer = LayoutRenderer('')
        self.request.wrapped_body = 'View: test'
        self.request.wrapped_response = self.request.response

        res = renderer(context, self.request).body
        self.assertTrue('<div>View: test</div>' in text_(res))

    def test_layout_for_route(self):
        from ptah.layout import query_layout, LayoutRenderer

        self.config.add_route('test-route', '/test/', use_global_views=False)
        ptah.layout.register('test', route_name='test-route')
        self.init_ptah()

        layout, context = query_layout(None, Context(), self.request, 'test')
        self.assertIsNone(layout)

        request_iface = self.registry.getUtility(
            IRouteRequest, name='test-route')
        self.request.request_iface = request_iface

        layout = query_layout(None, Context(), self.request, 'test')
        self.assertIsNotNone(layout)

    def test_layout_for_route_global_views(self):
        from ptah.layout import query_layout

        self.config.add_route('test-route', '/test/', use_global_views=False)
        ptah.layout.register('test', use_global_views=True)
        self.init_ptah()

        request_iface = self.registry.getUtility(
            IRouteRequest, name='test-route')
        self.request.request_iface = request_iface

        layout, context = query_layout(object(), object(), self.request, 'test')
        self.assertIsNotNone(layout)

    def test_layout_root(self):
        from ptah.layout import query_layout

        class Root1(object):
            pass

        class Root2(object):
            pass

        ptah.layout.register('test', root=Root1)
        self.init_ptah()

        layout, context = query_layout(Root1(), object(), self.request, 'test')
        self.assertIsNotNone(layout)

        layout, context = query_layout(Root2(), object(), self.request, 'test')
        self.assertIsNone(layout)

    def test_layout_chain_multi_level(self):
        class Layout1(ptah.View):
            """ """
        class Layout2(ptah.View):
            """ """
        class Layout3(ptah.View):
            """ """

        class Context1(object):
            """ """
        class Context2(object):
            """ """
        class Context3(object):
            """ """

        ptah.layout.register('l1', view=Layout1, context=Context1)
        ptah.layout.register('l1', view=Layout2, context=Context2, parent='l1')
        ptah.layout.register('l3', view=Layout3, context=Context3, parent='l1')
        self.init_ptah()

        root = Root()
        context1 = Context1()
        context2 = Context2()
        context3 = Context3()

        context1.__parent__ = root
        context2.__parent__ = context1
        context3.__parent__ = context2

        from ptah.layout import query_layout_chain
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


class Context(object):

    def __init__(self, parent=None):
        self.__parent__ = parent


class Context2(object):

    def __init__(self, parent=None):
        self.__parent__ = parent


class Root(Context):
    pass
