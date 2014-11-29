from webtest import TestApp
from pyramid.response import Response
from ptah.testing import PtahTestCase


class TestStaticConfig(PtahTestCase):

    _include = False
    _init_ptah = False

    def test_static_config(self):
        request = self.make_request()

        self.assertFalse(hasattr(self.config, 'init_static_components'))
        self.assertFalse(hasattr(self.config, 'add_static_component'))
        self.assertFalse(hasattr(request, 'include'))

        self.init_ptah()
        request = self.make_request()

        self.assertTrue(hasattr(self.config, 'init_static_components'))
        self.assertTrue(hasattr(self.config, 'add_static_component'))
        self.assertTrue(hasattr(request, 'include'))


class TestStatic(PtahTestCase):

    _init_bowerstatic = False

    def test_static_init_components(self):

        self.config.init_static_components()

        self.assertIn('components',
                      self.config.registry.bower._component_collections)
        self.assertIn('local',
                      self.config.registry.bower._component_collections)

    def test_static_init_custom_components(self):

        self.config.init_static_components(
            name='testcomponents',
            path='ptah:bowerstatic/tests/bower_components')

        self.assertIn('testcomponents',
                      self.config.registry.bower._component_collections)
        self.assertIn('local',
                      self.config.registry.bower._component_collections)

    def test_static_add_local_component(self):

        self.config.init_static_components()
        self.config.add_static_component(
            'ptah:bowerstatic/tests/local_component')

        local = self.config.registry.bower._component_collections['local']

        self.assertIn('myapp', local._components)


class TestRequestInclude(PtahTestCase):

    _init_bowerstatic = False

    def _get_response(self):
        app = self.config.make_wsgi_app()

        c = TestApp(app)
        response = c.get('/')
        return response

    def test_include(self):
        def view(request):
            request.include('jquery')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.init_static_components()

        response = self._get_response()

        self.assertEquals(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" '
            b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
            b'</script></head><body></body></html>'))

    def test_include_in_template(self):
        def view(request):
            request.include('jquery')
            return {}

        self.config.add_route('view', '/')
        self.config.add_view(
            view, route_name='view',
            renderer='ptah:bowerstatic/tests/templates/index.pt')
        self.config.init_static_components()

        response = self._get_response()

        self.assertIn(
            b'<script type="text/javascript" '
            b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
            b'</script>', response.body)

    def test_include_error(self):
        from simia.static import Error

        self.config.init_static_components(
            name='testcomponents',
            path='ptah:bowerstatic/tests/bower_components')

        self.assertRaises(Error, self.request.include, 'bootstrap')

    def test_include_custom_components(self):
        def view(request):
            request.include('jquery')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.init_static_components(
            name='testcomponents',
            path='ptah:bowerstatic/tests/bower_components')

        response = self._get_response()

        self.assertEquals(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" '
            b'src="/bowerstatic/testcomponents/jquery/2.1.1/dist/jquery.js">'
            b'</script></head><body></body></html>'))


    def test_include_local_component(self):
        def view(request):
            request.include('myapp')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.init_static_components()
        self.config.add_static_component(
            'ptah:bowerstatic/tests/local_component', '1.0.0')

        response = self._get_response()

        self.assertEquals(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" src='
            b'"/bowerstatic/components/jquery/2.1.1/dist/jquery.js"></script>\n'
            b'<script type="text/javascript" '
            b'src="/bowerstatic/local/myapp/1.0.0/dist/myapp.js"></script>'
            b'</head><body></body></html>'))
