""" renderers tests """
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

from memphis import config, view
from memphis.view.renderers import Renderer, JSONRenderer, SimpleRenderer

from base import Base, Context


class RendererBase(Base):
    pass


class TestSimpleRenderer(Base):

    def test_renderer_simple(self):
        def viewFactory(context, request):
            return None, 'test'

        r = SimpleRenderer()
        res = r(Context(), self.request, viewFactory)

        self.assertTrue(isinstance(res, Response))
        self.assertEqual(res.body, 'test')
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.content_type, 'text/html')

    def test_renderer_simple_return_response(self):
        resp = HTTPFound()
        def viewFactory(context, request):
            return None, resp

        r = SimpleRenderer()
        res = r(Context(), self.request, viewFactory)

        self.assertIs(res, resp)

    def test_renderer_simple_raise_response(self):
        resp = HTTPFound()
        def viewFactory(context, request):
            raise resp

        r = SimpleRenderer()
        res = r(Context(), self.request, viewFactory)

        self.assertIs(res, resp)

    def test_renderer_simple_bind(self):
        def viewFactory(context, request):
            return None, 'test'

        r = SimpleRenderer(content_type='text/plain').bind(viewFactory)
        res = r(Context(), self.request)

        self.assertTrue(isinstance(res, Response))
        self.assertEqual(res.body, 'test')
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.content_type, 'text/plain')

    def test_renderer_simple_with_layout(self):
        class Layout(view.Layout):
            def render(self, content):
                return '<html>%s</html>'%content

        view.registerLayout('test', klass=Layout)
        self._init_memphis()

        def viewFactory(context, request):
            return None, 'test'

        # renderer layout is different
        r = SimpleRenderer('')
        res = r(Context(), self.request, viewFactory)
        self.assertEqual(res.body, 'test')

        # layout is 'test'
        r = SimpleRenderer('test')
        res = r(Context(), self.request, viewFactory)
        self.assertEqual(res.body, '<html>test</html>')

    def test_renderer_simple_change_response_attrs(self):
        def viewFactory(context, request):
            request.response.status = 202
            request.response.content_type = 'text/plain'
            return None, 'test'

        r = SimpleRenderer()
        res = r(Context(), self.request, viewFactory)

        self.assertEqual(res.body, 'test')
        self.assertEqual(res.status, '202 Accepted')
        self.assertEqual(res.content_type, 'text/plain')


class TestJSONRenderer(RendererBase):

    def test_renderer_json(self):
        def viewFactory(context, request):
            return None, {'test': 1}

        r = JSONRenderer()
        res = r(Context(), self.request, viewFactory)

        self.assertTrue(isinstance(res, Response))
        self.assertEqual(res.body, '{"test": 1}')
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.content_type, 'text/json')

    def test_renderer_json_ct(self):
        def viewFactory(context, request):
            return None, {'test': 1}

        r = JSONRenderer('application/javascript')
        res = r(Context(), self.request, viewFactory)

        self.assertTrue(isinstance(res, Response))
        self.assertEqual(res.body, '{"test": 1}')
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.content_type, 'application/javascript')

    def test_renderer_json_bind(self):
        def viewFactory(context, request):
            return None, {'test': 1}

        r = JSONRenderer('application/javascript').bind(viewFactory)
        res = r(Context(), self.request)

        self.assertEqual(res.body, '{"test": 1}')


class TestTmplRenderer(RendererBase):

    def test_renderer_tmpl(self):
        def viewFactory(context, request):
            return None, {}

        r = Renderer(template=view.template('templates/test.pt'))
        res = r(Context(), self.request, viewFactory)

        self.assertTrue(isinstance(res, Response))
        self.assertEqual(res.body, '<div>My snippet</div>\n')
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.content_type, 'text/html')

    def test_renderer_tmpl_return_response(self):
        resp = Response()
        def viewFactory(context, request):
            return None, resp

        def template(**kw):
            """ """

        r = Renderer(template=template)
        res = r(Context(), self.request, viewFactory)

        self.assertIs(res, resp)

    def test_renderer_tmpl_raise_response(self):
        resp = HTTPFound()
        def viewFactory(context, request):
            raise resp

        def template(**kw):
            """ """
        
        r = Renderer(template=template)
        res = r(Context(), self.request, viewFactory)

        self.assertIs(res, resp)

    def test_renderer_tmpl_extra_params(self):
        def viewFactory(context, request):
            return None, {'test': 1}

        def template(**kw):
            return 'test: %s'%kw['test']

        r = Renderer(template=template)
        res = r(Context(), self.request, viewFactory)
        self.assertEqual(res.body, 'test: 1')

    def test_renderer_tmpl_extra_params_none(self):
        def viewFactory(context, request):
            return None, None

        r = Renderer(template=view.template('templates/test.pt'))
        res = r(Context(), self.request, viewFactory)
        self.assertEqual(res.body, '<div>My snippet</div>\n')

    def test_renderer_tmpl_extra_params_non_dict(self):
        def viewFactory(context, request):
            return None, [1,2]

        r = Renderer(template=view.template('templates/test.pt'))
        r(Context(), self.request, viewFactory)

    def test_renderer_tmpl_with_layout(self):
        class Layout(view.Layout):
            def render(self, content):
                return '<html>%s</html>'%content

        view.registerLayout('test', klass=Layout)
        self._init_memphis()

        def viewFactory(context, request):
            return None, {}

        # renderer layout is different
        r = Renderer(view.template('templates/test.pt'), '')
        res = r(Context(), self.request, viewFactory)
        self.assertEqual(res.body, '<div>My snippet</div>\n')

        # layout is 'test'
        config.cleanUp()
        r = Renderer(view.template('templates/test.pt'), 'test')
        res = r(Context(), self.request, viewFactory)
        self.assertEqual(res.body, '<html><div>My snippet</div>\n</html>')

    def test_renderer_tmpl_change_response_attrs(self):
        def viewFactory(context, request):
            request.response.status = 202
            request.response.content_type = 'text/plain'
            return None, None

        r = Renderer(view.template('templates/test.pt'))
        res = r(Context(), self.request, viewFactory)

        self.assertEqual(res.body, '<div>My snippet</div>\n')
        self.assertEqual(res.status, '202 Accepted')
        self.assertEqual(res.content_type, 'text/plain')
