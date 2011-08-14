""" base class """
import unittest
from memphis import config
from pyramid import testing
from pyramid.threadlocal import manager


class Base(unittest.TestCase):

    def _makeRequest(self, environ=None):
        from pyramid.request import Request
        if environ is None:
            environ = self._makeEnviron()
        return Request(environ)

    def _makeEnviron(self, **extras):
        environ = {
            'wsgi.url_scheme':'http',
            'wsgi.version':(1,0),
            'PATH_INFO': '/',
            'SERVER_NAME':'localhost',
            'SERVER_PORT':'8080',
            'REQUEST_METHOD':'GET',
            }
        environ.update(extras)
        return environ

    def _setup_pyramid(self):
        testing.cleanUp()

        self.request = request = testing.DummyRequest()
        request.params = {}
        self.p_config = testing.setUp(request=request)
        self.p_config.get_routes_mapper()

    def _setup_memphis(self):
        config.begin()
        config.loadPackage('memphis.view')
        config.commit()

    def _setRequest(self, request):
        self.request = request
        self.p_config.end()
        self.p_config.begin(request)

    def setUp(self):
        self._setup_pyramid()
        self._setup_memphis()

    def tearDown(self):
        config.cleanUp()
        testing.tearDown()
        testing.cleanUp()
