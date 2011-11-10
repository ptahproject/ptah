""" base class """
import unittest
import sqlahelper
import transaction
from ptah import config
from pyramid import testing
from pyramid.threadlocal import manager


class Base(unittest.TestCase):

    _settings = {'sqla.url': 'sqlite://',
                 'auth.secret': 'test'}

    def _makeRequest(self, environ=None): #pragma: no cover
        from pyramid.request import Request
        if environ is None:
            environ = self._makeEnviron()
        return Request(environ)

    def _makeEnviron(self, **extras): #pragma: no cover
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

    def _init_ptah(self, settings=None, handler=None, *args, **kw):
        if settings is None:
            settings = self._settings
        config.initialize(self.config, ('ptah', self.__class__.__module__),
                          initsettings=False)
        config.initialize_settings(settings, self.config)

        # create sql tables
        Base = sqlahelper.get_base()
        Base.metadata.drop_all()
        Base.metadata.create_all()
        transaction.commit()

    def _setup_pyramid(self):
        self.request = request = self._makeRequest()
        self.config = testing.setUp(request=request)
        self.config.get_routes_mapper()
        self.registry = self.config.registry
        self.request.registry = self.config.registry

    def _setRequest(self, request): #pragma: no cover
        self.request = request
        self.config.end()
        self.config.begin(request)
        request.registry = self.config.registry

    def setUp(self):
        self._setup_pyramid()
        self._init_ptah()

    def tearDown(self):
        transaction.abort()
        config.cleanup_system()
        sm = self.config
        sm.__init__('base')
        testing.tearDown()

        Session = sqlahelper.get_session()
        Session.expunge_all()
