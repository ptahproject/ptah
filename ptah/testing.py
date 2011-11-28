""" base class """
import unittest
import sqlahelper
import sqlalchemy
import transaction
from pyramid import testing
from pyramid.interfaces import \
     IRequest, IAuthenticationPolicy, IAuthorizationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy

import ptah
from ptah import config


class PtahTestCase(unittest.TestCase):

    _init_ptah = True
    _init_sqla = True
    _init_auth = False
    _cleanup_mod = True
    _settings = {}
    _environ = {
        'wsgi.url_scheme':'http',
        'wsgi.version':(1,0),
        'SCRIPT_NAME': '',
        'PATH_INFO': '/',}

    def make_request(self, environ=None, request_iface=IRequest, **kwargs):
        if environ is None:
            environ=self._environ
        request = testing.DummyRequest(environ=environ, **kwargs)
        request.request_iface = IRequest
        return request

    def init_ptah(self, handler=None, *args, **kw):
        config.initialize(
            self.config, ('ptah', self.__class__.__module__),
            initsettings = False)
        config.initialize_settings(self.registry.settings, self.config)

        if self._init_sqla:
            # create sql tables
            Base = sqlahelper.get_base()
            Base.metadata.drop_all()
            Base.metadata.create_all()
            transaction.commit()

        config.start(self.config)

    def init_pyramid(self):
        self.request = request = self.make_request()
        self.config = testing.setUp(request=request, settings=self._settings)
        self.config.include('ptah')
        self.config.get_routes_mapper()
        self.registry = self.config.registry
        self.request.registry = self.registry

        if self._init_auth:
            policy = AuthTktAuthenticationPolicy(
                'secret', callback= ptah.get_local_roles)

            self.registry.registerUtility(
                policy, IAuthenticationPolicy)

            self.registry.registerUtility(
                ACLAuthorizationPolicy(), IAuthorizationPolicy)

    def setUp(self):
        if self._init_sqla:
            try:
                engine = sqlahelper.get_engine()
            except: # pragma: no cover
                engine = sqlalchemy.engine_from_config(
                    {'sqlalchemy.url': 'sqlite://'})
                sqlahelper.add_engine(engine)

        self.init_pyramid()

        if self._init_ptah: # pragma: no cover
            self.init_ptah()

    def tearDown(self):
        if self._cleanup_mod:
            config.cleanup_system(self.__class__.__module__)
        else:
            config.cleanup_system()

        testing.tearDown()
        transaction.abort()
