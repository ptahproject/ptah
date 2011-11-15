import unittest
import sqlahelper
import sqlalchemy
import transaction
from pyramid import testing
from pyramid.interfaces import IAuthenticationPolicy, IAuthorizationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy

import ptah
from ptah import config


class Base(unittest.TestCase):

    _settings = {'sqla.url': 'sqlite://',
                 'sqla.cache': False}

    def _makeRequest(self, environ=None):
        from pyramid.request import Request
        if environ is None:
            environ = self._makeEnviron()
        request = Request(environ)
        request.registry = self.p_config.registry
        return request

    def _makeEnviron(self, **extras):
        environ = {
            'wsgi.url_scheme':'http',
            'wsgi.version':(1,0),
            'PATH_INFO': '/',
            'SCRIPT_NAME': '',
            'SERVER_NAME':'localhost',
            'SERVER_PORT':'8080',
            'REQUEST_METHOD':'GET',
            }
        environ.update(extras)
        return environ

    def _init_ptah(self, settings=None, handler=None, *args, **kw):
        if settings is None:
            settings = self._settings
        config.initialize(
            self.p_config, ('ptah', self.__class__.__module__),
            initsettings = False)
        config.initialize_settings(settings, self.p_config)

        # create sql tables
        Base = sqlahelper.get_base()
        Base.metadata.drop_all()
        Base.metadata.create_all()
        transaction.commit()

    def _setup_pyramid(self):
        self.request = request = testing.DummyRequest()
        request.params = {}
        self.p_config = testing.setUp(request=request)
        self.p_config.get_routes_mapper()
        self.registry = self.p_config.registry
        self.request.registry = self.p_config.registry

        policy = AuthTktAuthenticationPolicy(
            'secret', callback= ptah.get_local_roles)

        self.registry.registerUtility(
            policy, IAuthenticationPolicy)

        self.registry.registerUtility(
            ACLAuthorizationPolicy(), IAuthorizationPolicy)

    def _setup_ptah(self):
        self._init_ptah()

    def _setRequest(self, request):
        self.request = request
        self.p_config.end()
        self.p_config.begin(request)

    def setUp(self):
        try:
            engine = sqlahelper.get_engine()
        except:
            engine = sqlalchemy.engine_from_config(
                {'sqlalchemy.url': 'sqlite://'})
            sqlahelper.add_engine(engine)

        self._setup_pyramid()
        self._setup_ptah()

    def tearDown(self):
        #config.cleanup_system(self.__class__.__module__)
        config.cleanup_system()

        sm = self.p_config
        sm.__init__('base')
        testing.tearDown()

        Session = sqlahelper.get_session()
        Session.expunge_all()
