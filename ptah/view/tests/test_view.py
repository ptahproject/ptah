""" view tests """
from zope import interface
from pyramid.interfaces import IView, IRequest, IRouteRequest
from pyramid.interfaces import IViewClassifier
from pyramid.interfaces import IExceptionViewClassifier
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.httpexceptions import HTTPForbidden, HTTPFound

from ptah import config, view

from base import Base, Context


class BaseView(Base):

    def _setup_ptah(self):
        pass

    def _view(self, name, context, request):
        adapters = self.registry.adapters

        view_callable = adapters.lookup(
            (IViewClassifier,
             interface.providedBy(request),
             interface.providedBy(context)),
            IView, name=name, default=None)

        return view_callable(context, request)


class TestView(BaseView):

    def test_view_register_errs(self):
        self.assertRaises(
            ValueError, view.register_view, 'test.html', None)

        self.assertRaises(
            ValueError, view.register_view, 'test.html', {})

    def test_view_register_view(self):
        class MyView(view.View):
            def render(self):
                return '<html>view</html>'

        view.register_view('index.html', MyView)
        self._init_ptah()

        context = Context()
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.status, '200 OK')
        self.assertEqual(v.content_type, 'text/html')
        self.assertEqual(v.body, '<html>view</html>')

    def test_view_register_declarative(self):
        global MyView

        class MyView(view.View):
            view.pview('index.html')

            def render(self):
                return '<html>view</html>'

        self._init_ptah()

        context = Context()
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.status, '200 OK')
        self.assertEqual(v.content_type, 'text/html')
        self.assertEqual(v.body, '<html>view</html>')

    def test_view_register_view_err1(self):
        # default 'render' implementation
        class MyView(view.View):
            pass

        view.register_view('index.html', MyView, Context)
        self._init_ptah()

        context = Context()
        self.assertTrue(
            view.render_view('index.html', context,
                            self.request).content_length ==0)

    def test_view_register_view_layout(self):
        class MyLayout(view.Layout):
            def render(self, rendered):
                return '<html>%s</html>'%rendered

        class MyView(view.View):
            def render(self):
                return 'test'

        view.register_view('index.html', MyView, Context)
        view.register_layout('', Context, klass=MyLayout)
        self._init_ptah()

        context = Context()
        res = view.render_view('index.html', context, self.request)
        self.assertTrue('<html>test</html>' in res.body)

    def test_view_register_view_disable_layout1(self):
        class MyLayout(view.Layout):
            def render(self, rendered):
                return '<html>%s</html>'%rendered

        class MyView(view.View):
            def render(self):
                return 'test'

        view.register_view('index.html', MyView, Context, layout=None)
        view.register_layout('', Context, klass=MyLayout)
        self._init_ptah()

        context = Context()
        res = view.render_view('index.html', context, self.request)
        self.assertEqual(res.body, 'test')

        v = MyView(None, self.request)
        self.assertEqual(MyLayout(v, self.request).render(
                v.render()), '<html>test</html>')

    def test_view_custom_response(self):
        class MyView(view.View):
            def render(self):
                response = self.request.response
                response.status = '202'
                return 'test'

        view.register_view('index.html', MyView, Context)
        self._init_ptah()

        res = view.render_view('index.html', Context(), self.request)
        self.assertEqual(res.status, '202 Accepted')
        self.assertEqual(res.body, 'test')

    def test_view_custom_return_response(self):
        class MyView(view.View):
            def render(self):
                response = self.request.response
                response.status = '202'
                response.body = 'test response'
                return response

        view.register_view('index.html', MyView, Context)
        self._init_ptah()

        res = view.render_view('index.html', Context(), self.request)
        self.assertEqual(res.status, '202 Accepted')
        self.assertEqual(res.body, 'test response')

    def test_view_httpresp_from_update(self):
        class MyView(view.View):
            def update(self):
                raise HTTPForbidden()

        view.register_view('index.html', MyView, Context,
                          template = view.template('templates/test.pt'))
        self._init_ptah()

        resp = view.render_view('index.html', Context(), self.request)
        self.assertIsInstance(resp, HTTPForbidden)

    def test_view_httpresp_from_update_return(self):
        class MyView(view.View):
            def update(self):
                return HTTPForbidden()

        view.register_view('index.html', MyView, Context,
                          template = view.template('templates/test.pt'))
        self._init_ptah()

        resp = view.render_view('index.html', Context(), self.request)
        self.assertIsInstance(resp, HTTPForbidden)

    def test_view_httpresp_from_render(self):
        class MyView(view.View):
            def render(self):
                raise HTTPFound()

        view.register_view('index.html', MyView, Context)
        self._init_ptah()

        resp = view.render_view('index.html', Context(), self.request)
        self.assertIsInstance(resp, HTTPFound)

    def test_view_with_template(self):
        view.register_view(
            'index.html', view.View, Context,
            template=view.template('ptah.view.tests:templates/test.pt'))

        self._init_ptah()

        res = view.render_view('index.html', Context(), self.request)
        self.assertEqual(res.body.strip(), '<div>My snippet</div>')

    def test_view_with_decorator(self):
        def deco(func):
            def func(context, request):
                return 'decorator'
            return func

        global DecoView

        @deco
        class DecoView(view.View):
            view.pview('index.html', Context)

        self._init_ptah()

        res = view.render_view('index.html', Context(), self.request)
        self.assertEqual(res.body, 'decorator')

    def test_view_register_view_class_requestonly(self):
        class MyView(object):
            def __init__(self, request):
                self.request = request

            def render(self):
                return '<html>view: %s</html>'%(self.request is not None)

        view.register_view('index.html', MyView)
        self._init_ptah()

        context = Context()
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.body, '<html>view: True</html>')

    def test_view_register_view_function(self):
        def render(context, request):
            return '<html>context: %s</html>'%(context is not None)

        view.register_view('index.html', render)
        self._init_ptah()

        context = Context()
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.body, '<html>context: True</html>')

    def test_view_register_view_function_requestonly(self):
        def render(request):
            return '<html>request: %s</html>'%(request is not None)

        view.register_view('index.html', render)
        self._init_ptah()

        context = Context()
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.body, '<html>request: True</html>')

    def test_view_register_view_function_with_template(self):
        def render(context, request):
            return {}

        view.register_view('index.html', render,
                          template = view.template('templates/test.pt'))
        self._init_ptah()

        context = Context()
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.body.strip(), '<div>My snippet</div>')

    def test_view_register_view_function_requestonly_template(self):
        def render(request):
            return {}

        view.register_view('index.html', render,
                          template = view.template('templates/test.pt'))
        self._init_ptah()

        context = Context()
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.body.strip(), '<div>My snippet</div>')

    def test_view_register_callable_permission(self):
        def render(request):
            return '<html>Secured view</html>'

        allowed = False
        def check_permission(context, request):
            return allowed

        view.register_view('index.html', render,
                          permission = check_permission)

        self._init_ptah()

        context = Context()

        resp = self._view('index.html', context, self.request)

        self.assertIsInstance(resp, HTTPForbidden)

        allowed = True
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.body, '<html>Secured view</html>')

    def test_view_register_secured_view(self):
        from ptah.view.renderers import \
            default_checkpermission, set_checkpermission

        def render(request):
            return '<html>Secured view</html>'

        view.register_view('index.html', render,
                          permission = 'Protected')

        self._init_ptah()

        set_checkpermission(default_checkpermission)

        context = Context()
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.body, '<html>Secured view</html>')

        class SimpleAuth(object):
            interface.implements(IAuthenticationPolicy)

            def effective_principals(self, request):
                return (1,2)

        class Authz(object):
            interface.implements(IAuthorizationPolicy)

            allowed = False

            def permits(self, context, princials, permission):
                return self.allowed

        self.registry.registerUtility(SimpleAuth(), IAuthenticationPolicy)
        self.registry.registerUtility(Authz(), IAuthorizationPolicy)

        set_checkpermission(default_checkpermission)

        context = Context()
        resp = self._view('index.html', context, self.request)
        self.assertIsInstance(resp, HTTPForbidden)

        Authz.allowed = True
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.body, '<html>Secured view</html>')

    def test_view_function(self):
        @view.pview('index.html')
        def render(request):
            return '<html>content</html>'

        self._init_ptah()

        context = Context()
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.body, '<html>content</html>')

    def test_view_custom_class(self):
        global View
        class View(object):
            view.pview('index.html')

            def __init__(self, request):
                self.request = request
                self.updated = False
            def update(self):
                self.updated = True
            def render(self):
                return str(self.updated)

        self._init_ptah()

        context = Context()
        v = self._view('index.html', context, self.request)
        self.assertEqual(v.body, 'True')

    def test_view_for_exception(self):
        @view.pview(context=HTTPForbidden, layer='test')
        def render(request):
            return '<html>Forbidden</html>'

        self._init_ptah()

        context = HTTPForbidden()

        adapters = self.registry.adapters

        view_callable = adapters.lookup(
            (IExceptionViewClassifier,
             interface.providedBy(self.request),
             interface.providedBy(context)),
            IView, name='', default=None)

        v = view_callable(context, self.request)
        self.assertEqual(v.body, '<html>Forbidden</html>')

    def test_view_for_route(self):
        view.register_route('test-route', '/test/')

        @view.pview(route='test-route')
        def render(request):
            return '<html>Route view</html>'

        self._init_ptah()

        request_iface = self.registry.getUtility(
            IRouteRequest, name='test-route')

        interface.directlyProvides(self.request, request_iface)

        v = self._view('', None, self.request)
        self.assertEqual(v.body, '<html>Route view</html>')


class TestRouteRegistration(BaseView):

    def test_view_route(self):
        view.register_route('test-route', '/test/')
        self._init_ptah()

        request_iface = self.registry.getUtility(
            IRouteRequest, name='test-route')

        self.assertIsNotNone(request_iface)

    def test_view_route_global_view(self):
        view.register_route('test-route', '/test/', use_global_views=True)
        self._init_ptah()

        request_iface = self.registry.getUtility(
            IRouteRequest, name='test-route')

        self.assertTrue(request_iface.isOrExtends(IRequest))

    def test_view_route_conflict(self):
        view.register_route('test-route', '/test/')
        view.register_route('test-route', '/test2/')
        self.assertRaises(config.ConflictError, self._init_ptah)


class TestViewView(BaseView):

    def test_view_render(self):

        class MyView(view.View):
            def template(self, **kw):
                return 'MyView rendered'

        self.assertEqual(MyView(None, None).render(), 'MyView rendered')
