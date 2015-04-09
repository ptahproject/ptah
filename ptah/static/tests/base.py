from unittest import TestCase
from webtest import TestApp

from pyramid import testing
from pyramid.interfaces import IRequest
from pyramid.interfaces import IRequestExtensions


class BaseTestCase(TestCase):

    _includes = ('ptah.static',)
    _auto_commit = True
    _settings = {}
    _environ = {
        'wsgi.url_scheme': 'http',
        'wsgi.version': (1, 0),
        'HTTP_HOST': 'example.com',
        'SCRIPT_NAME': '',
        'PATH_INFO': '/'}
    registry = None

    def setUp(self):
        self.config = testing.setUp(
            settings=self._settings, autocommit=self._auto_commit)
        self.init_request_extensions(self.config.registry)
        self.config.get_routes_mapper()

        for pkg in self._includes:
            self.config.include(pkg)

        self.registry = self.config.registry
        self.request = self.make_request()

        self.config.begin(self.request)
        self.config.scan(self.__class__.__module__)

    def make_request(self, registry=None, environ=None,
                     request_iface=IRequest, **kwargs):
        if registry is None:
            registry = self.registry
        if environ is None:
            environ = self._environ
        request = testing.DummyRequest(environ=dict(environ), **kwargs)
        request.request_iface = IRequest
        request.registry = registry
        request._set_extensions(registry.getUtility(IRequestExtensions))
        return request

    def make_app(self):
        app = self.config.make_wsgi_app()
        return TestApp(app)

    def init_request_extensions(self, registry):
        from pyramid.config.factories import _RequestExtensions

        exts = registry.queryUtility(IRequestExtensions)
        if exts is None:
            exts = _RequestExtensions()
            registry.registerUtility(exts, IRequestExtensions)

    def tearDown(self):
        self.config.end()
        testing.tearDown()
