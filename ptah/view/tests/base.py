""" base class """
import unittest
from ptah import config
from pyramid import testing


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

    def _init_ptah(self, settings={}, handler=None, *args, **kw):
        config.initialize(self.p_config, ('ptah', self.__class__.__module__),
                          initsettings = False)
        config.initialize_settings(settings, self.p_config)
        config.start(self.p_config)

    def _setup_pyramid(self):
        self.request = request = testing.DummyRequest()
        request.params = {}
        self.p_config = testing.setUp(request=request)
        self.registry = self.p_config.registry
        self.request.registry = self.p_config.registry

    def _setup_ptah(self):
        config.initialize(self.p_config, ('ptah', self.__class__.__module__))

    def _setRequest(self, request):
        self.request = request
        self.p_config.end()
        self.p_config.begin(request)

    def setUp(self):
        self._setup_pyramid()
        self._setup_ptah()

    def tearDown(self):
        config.shutdown()
        config.cleanup_system(self.__class__.__module__)
        sm = self.p_config
        sm.__init__('base')
        testing.tearDown()


class Context(object):

    def __init__(self, parent=None, name=''):
        self.__name__ = name
        self.__parent__ = parent
