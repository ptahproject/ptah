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
from memphis.view.base import View

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

        return view_callable(context, request)

    def test_view_register_errs(self):
        self.assertRaises(
            ValueError, view.registerView, 'test.html', None)

        self.assertRaises(
            ValueError, view.registerView, 'test.html', {})

    def test_view_register_view(self):
        class MyView(view.View):
            def render(self):
                return '<html>view</html>'

        view.registerView('index.html', MyView)
        self._init_memphis()

        context = Context()
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.status, '200 OK')
        self.assertEqual(v.content_type, 'text/html')
        self.assertEqual(v.body, '<html>view</html>')

    def test_view_register_view_err1(self):
        # default 'render' implementation
        class MyView(view.View):
            pass

        view.registerView('index.html', MyView, Context)
        self._init_memphis()

        context = Context()
        self.assertTrue(
            view.renderView('index.html', context, 
                            self.request).content_length ==0)

    def test_view_register_view_layout(self):
        class MyLayout(view.Layout):
            def render(self, rendered):
                return '<html>%s</html>'%rendered

        class MyView(view.View):
            def render(self):
                return 'test'

        view.registerView('index.html', MyView, Context)
        view.registerLayout('', Context, klass=MyLayout)
        self._init_memphis()

        context = Context()
        res = view.renderView('index.html', context, self.request)
        self.assertTrue('<html>test</html>' in res.body)

    def test_view_register_view_disable_layout1(self):
        class MyLayout(view.Layout):
            def render(self, rendered):
                return '<html>%s</html>'%rendered

        class MyView(view.View):
            def render(self):
                return 'test'

        view.registerView('index.html', MyView, Context, layout=None)
        view.registerLayout('', Context, klass=MyLayout)
        self._init_memphis()

        context = Context()
        res = view.renderView('index.html', context, self.request)
        self.assertEqual(res.body, 'test')

        v = MyView(None, self.request)
        self.assertEqual(MyLayout(v, None, self.request).render(
                v.render()), '<html>test</html>')

    def test_view_custom_response(self):
        class MyView(view.View):
            def render(self):
                response = self.request.response
                response.status = '202'
                return 'test'

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

    def test_view_with_decorator(self):
        def deco(func):
            def func(context, request):
                return 'decorator'
            return func

        view.registerView(
            'index.html', view.View, Context, decorator = deco)

        self._init_memphis()

        res = view.renderView('index.html', Context(), self.request)
        self.assertEqual(res, 'decorator')


class Context(object):

    def __init__(self, parent=None):
        self.__parent__ = parent
