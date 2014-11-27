from webtest import TestApp
from pyramid.response import Response
from bowerstatic import Error

from ptah.testing import PtahTestCase


class TestBowerstaticInclude(PtahTestCase):

    _include = False
    _init_ptah = False

    def test_include(self):

        self.assertFalse(hasattr(self.config, 'init_bowerstatic'))
        self.assertFalse(hasattr(self.request, 'include'))

        self.config.include('ptah.bowerstatic')
        self.init_ptah()
        request = self.make_request()

        self.assertTrue(hasattr(self.config, 'init_bowerstatic'))
        self.assertTrue(hasattr(request, 'include'))


class TestRequestInclude(PtahTestCase):

    _init_ptah = False

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
        self.init_ptah()

        response = self._get_response()

        self.assertIn('jquery.js', str(response.body))

    def test_include_in_template(self):
        def view(request):
            request.include('jquery')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view',
                             renderer='ptah.bowerstatic:tests/index.pt')
        self.init_ptah()

        response = self._get_response()

        self.assertIn('jquery.js', str(response.body))
        
    def test_include_error(self):
        self.assertRaises(Error, self.request.include, 'jquery')
