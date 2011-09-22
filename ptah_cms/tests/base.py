""" base class """
import unittest
import pyramid_sqla
import transaction
from memphis import config
from pyramid import testing
from pyramid.threadlocal import manager
from zope.interface.registry import Components


class Base(unittest.TestCase):

    _settings = {'sqla.url': 'sqlite://',
                 'sqla.cache': False}

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

    def _init_memphis(self, settings=None, handler=None, *args, **kw):
        if settings is None:
            settings = self._settings
        config.initialize(('ptah_cms', self.__class__.__module__),
                          reg = Components('test'))
        config.initializeSettings(settings, self.p_config)

        # create sql tables
        Base = pyramid_sqla.get_base()
        Base.metadata.drop_all()
        transaction.commit()
        Base.metadata.create_all()
        transaction.commit()

    def _setup_pyramid(self):
        self.request = request = testing.DummyRequest()
        request.params = {}
        self.p_config = testing.setUp(request=request)
        self.p_config.get_routes_mapper()

    def _setup_memphis(self):
        self._init_memphis()

    def _setRequest(self, request):
        self.request = request
        self.p_config.end()
        self.p_config.begin(request)

    def setUp(self):
        self._setup_pyramid()
        self._setup_memphis()

    def tearDown(self):
        config.cleanUp()
        sm = self.p_config
        sm.__init__('base')
        testing.tearDown()
