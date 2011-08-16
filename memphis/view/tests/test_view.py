""" view tests """
import sys, unittest
from zope import interface, component
from zope.configuration.config import ConfigurationExecutionError

from webob.exc import HTTPForbidden, HTTPNotFound, HTTPFound
from webob.response import Response
from pyramid.interfaces import IView, IRequest
from pyramid.interfaces import IViewClassifier
from pyramid.interfaces import IAuthenticationPolicy

from memphis import config, view
from memphis.config import api
from memphis.view import meta
from memphis.view.view import View, SimpleView

from base import Base

       
class TestView(Base):

    def _setup_memphis(self):
        pass

    def _init_memphis(self, settings={}, handler=None, *args, **kw):
        config.begin()
        config.loadPackage('memphis.view')
        config.addPackage('memphis.view.tests.test_view')
        if handler is not None:
            handler(*args, **kw)
        config.commit()
        config.initializeSettings(settings, self.p_config)

    def _view(self, name, context, request):
        adapters = component.getSiteManager().adapters

        view_callable = adapters.lookup(
            (IViewClassifier, 
             interface.providedBy(request), 
             interface.providedBy(context)),
            IView, name=name, default=None)

        return view_callable.factory(context, request)

    def test_view_register_err1(self):
        self.assertRaises(
            ValueError, view.registerView, 'test.html', klass=None)

    def test_view_register_err2(self):
        class MyView(object):
            pass

        self.assertRaises(
            ValueError, view.registerView, 'test.html', MyView)

    def test_view_register_simpleview(self):
        class MyView(view.SimpleView):
            def __call__(self):
                return '<html>view</html>'

        view.registerView('index.html', MyView)
        self._init_memphis()

        context = Context()
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.response_status, 200)
        self.assertEqual(v.response_headers, [])
        self.assertEqual(v(), '<html>view</html>')

    def test_view_register_simpleview_err1(self):
        # __call__ has to be implemented
        class MyView(view.SimpleView):
            pass

        view.registerView('index.html', MyView, Context)
        self._init_memphis()

        context = Context()
        self.assertRaises(
            HTTPNotFound,
            view.renderView, 'index.html', context, self.request)

    def test_view_register_simpleview_err2(self):
        # can't register same class to different views
        class MyView(view.SimpleView):
            pass

        view.registerView('index.html', MyView, Context)
        view.registerView('index1.html', MyView, Context)
        self.assertRaises(ConfigurationExecutionError, self._init_memphis)

    def test_view_register_view(self):
        class MyView(view.View):
            def render(self):
                return '<html>test</html>'

        view.registerView('index.html', MyView, Context)
        self._init_memphis()

        context = Context()
        res = view.renderView('index.html', context, self.request)
        self.assertTrue(isinstance(res, Response))
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.body, '<html>test</html>')

    def test_view_register_view_layout(self):
        class MyLayout(view.Layout):
            def render(self):
                return '<html>%s</html>'%self.view.render()

        class MyView(view.View):
            def render(self):
                return 'test'

        view.registerView('index.html', MyView, Context)
        view.registerLayout('', Context, klass=MyLayout)
        self._init_memphis()

        context = Context()
        res = view.renderView('index.html', context, self.request)
        self.assertEqual(res.body, '<html>test</html>')

    def test_view_register_view_disable_layout1(self):
        class MyLayout(view.Layout):
            def render(self):
                return '<html>%s</html>'%self.view.render()

        class MyView(view.View):
            def render(self):
                return 'test'

        view.registerView('index.html', MyView, Context, layout=None)
        view.registerLayout('', Context, klass=MyLayout)
        self._init_memphis()

        context = Context()
        res = view.renderView('index.html', context, self.request)
        self.assertEqual(res.body, 'test')

    def test_view_register_view_disable_layout2(self):
        class MyLayout(view.Layout):
            def render(self):
                return '<html>%s</html>'%self.view.render()

        class MyView(view.View):
            layout = None
            def render(self):
                return 'test'

        view.registerView('index.html', MyView, Context)
        view.registerLayout('', Context, klass=MyLayout)
        self._init_memphis()

        context = Context()
        res = view.renderView('index.html', context, self.request)
        self.assertEqual(res.body, 'test')

    def test_view_view_disable_layout3(self):
        class MyLayout(view.Layout):
            def render(self):
                return '<html>%s</html>'%self.view.render()

        class MyView(view.View):
            layout = None
            def render(self):
                return 'test'

        view.registerView('index.html', MyView, Context, layout='test')
        view.registerLayout('test', Context, klass=MyLayout)
        self._init_memphis()

        res = view.renderView('index.html', Context(), self.request)
        self.assertEqual(res.body, '<html>test</html>')

    def test_view_response_from_render(self):
        class MyView(view.View):
            response_status = '202'
            def render(self):
                return Response(body = 'test', 
                                status = self.response_status,
                                headerlist = self.response_headers)

        view.registerView('index.html', MyView, Context)
        self._init_memphis()

        res = view.renderView('index.html', Context(), self.request)
        self.assertEqual(res.status, '202 Accepted')
        self.assertEqual(res.body, 'test')

    def test_view_httpresp_from_update(self):
        class MyView(view.View):
            def update(self):
                raise HTTPForbidden()

        view.registerView('index.html', MyView, Context)
        self._init_memphis()

        res = view.renderView('index.html', Context(), self.request)
        self.assertTrue(isinstance(res, HTTPForbidden))

    def test_view_httpresp_from_render(self):
        class MyView(view.View):
            def update(self):
                raise HTTPFound()

        view.registerView('index.html', MyView, Context)
        self._init_memphis()

        res = view.renderView('index.html', Context(), self.request)
        self.assertTrue(isinstance(res, HTTPFound))

    def test_view_with_template(self):
        view.registerView(
            'index.html', view.View, Context,
            template=view.template('memphis.view.tests:templates/test.pt'))

        self._init_memphis()

        res = view.renderView('index.html', Context(), self.request)
        self.assertEqual(res.body, '<div>My pagelet</div>\n')

    def test_view_with_decoratr(self):
        def deco(func):
            def func(context, request):
                def func2():
                    return 'decorator'
                return func2
            return func

        view.registerView(
            'index.html', view.View, Context, decorator = deco)

        self._init_memphis()

        res = view.renderView('index.html', Context(), self.request)
        self.assertEqual(res, 'decorator')


class Context(object):

    def __init__(self, parent=None):
        self.__parent__ = parent
