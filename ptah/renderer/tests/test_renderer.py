import ptah.renderer
from ptah.testing import BaseTestCase


class TestRequestRenderers(BaseTestCase):

    _includes = ['ptah.renderer']

    def test_render_tmpl(self):
        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')

        text = self.request.render_tmpl('test:view', object()).strip()
        self.assertEqual(text, '<h1>Test</h1>')

    def test_render_tmpl_with_filter(self):
        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')

        _calls = []
        def _filter(context, request):
            _calls.append((context, request))
            return {}

        self.config.add_tmpl_filter('test:view', _filter)

        ob = object()
        text = self.request.render_tmpl('test:view', ob).strip()
        self.assertEqual(text, '<h1>Test</h1>')
        self.assertEqual(1, len(_calls))
        self.assertEqual((ob, self.request), _calls[0])

    def test_render_tmpl_ext(self):
        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')

        text = self.request.render_tmpl('test:view.lt', object()).strip()
        self.assertEqual(text, '<h1>Test</h1>')

    def test_render_tmpl_unknown(self):
        self.assertRaises(
            ValueError, self.request.render_tmpl, 'test:view')

        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')
        self.assertRaises(
            ValueError, self.request.render_tmpl, 'test:view2')

    def test_render_tmpl_customize(self):
        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')
        self.config.add_layer(
            'test', 'custom', path='ptah.renderer:tests/bundle/dir1/')

        text = self.request.render_tmpl('test:view', object()).strip()
        self.assertEqual(text, '<h2>Test</h2>')

    def test_template(self):
        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')

        from ptah.renderer.renderer import template
        tmpl = template('test:view')

        text = tmpl(self.request, object())
        self.assertEqual(text, '<h1>Test</h1>')

    def test_pyramid_renderer(self):
        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')

        from pyramid.renderers import render

        text = render('test:view.lt', {'context': object()}).strip()
        self.assertEqual(text, '<h1>Test</h1>')

    def test_pyramid_renderer_no_templates(self):
        """
        Raise ValueError if template can't be found.
        """
        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')

        from pyramid.renderers import render

        self.assertRaises(
            ValueError, render, 'test:view2.lt', {})

        self.assertRaises(
            ValueError, render, 'test1:view.lt', {})


class TestRender(BaseTestCase):

    _includes = ['ptah.renderer']

    def setUp(self):
        super(TestRender, self).setUp()

        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')

    def test_render(self):
        text = ptah.renderer.render(self.request, 'test:view').strip()
        self.assertEqual(text, '<h1>Test</h1>')

    def test_render_standard(self):
        """
        It is possible to use standard renderers as asset var
        """
        text = ptah.renderer.render(
            self.request, 'ptah.renderer:tests/dir1/view.pt')
        self.assertEqual(text, '<h1>Test</h1>')
