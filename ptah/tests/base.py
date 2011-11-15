""" base class """
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
                 'sqla.cache': False,
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

    def _init_ptah(self, handler=None, *args, **kw):
        config.initialize(
            self.p_config, ('ptah', self.__class__.__module__),
            initsettings = False)
        config.initialize_settings(self._settings, self.p_config)

        # create sql tables
        Base = sqlahelper.get_base()
        Base.metadata.drop_all()
        Base.metadata.create_all()
        transaction.commit()

    def _setup_pyramid(self):
        self.request = request = self._makeRequest()
        self.p_config = testing.setUp(request=request)
        self.p_config.get_routes_mapper()
        self.registry = self.p_config.registry
        self.request.registry = self.registry

        policy = AuthTktAuthenticationPolicy(
            'secret', callback= ptah.get_local_roles)

        self.registry.registerUtility(
            policy, IAuthenticationPolicy)

        self.registry.registerUtility(
            ACLAuthorizationPolicy(), IAuthorizationPolicy)

    def _setRequest(self, request): #pragma: no cover
        self.request = request
        self.p_config.end()
        self.p_config.begin(request)

    def setUp(self):
        try:
            engine = sqlahelper.get_engine()
        except: # pragma: no cover
            engine = sqlalchemy.engine_from_config(
                {'sqlalchemy.url': 'sqlite://'})
            sqlahelper.add_engine(engine)

        self._setup_pyramid()

    def tearDown(self):
        config.cleanup_system()
        sm = self.p_config
        sm.__init__('base')
        testing.tearDown()
