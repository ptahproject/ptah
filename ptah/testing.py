""" base class """
import sys
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

    _settings = {}
    _packages = ()
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

    def init_ptah(self, *args, **kw):
        self.registry.settings.update(self._settings)

        self.config.scan('ptah')
        self.config.commit()
        self.config.autocommit = True

        ptah.init_settings(self.config, self.registry.settings)

        if self._init_sqla:
            # create sql tables
            Base = sqlahelper.get_base()
            Base.metadata.drop_all()
            Base.metadata.create_all()
            transaction.commit()

    def init_pyramid(self):
        self.request = request = self.make_request()
        self.config = testing.setUp(
            request=request, settings=self._settings, autocommit=False)
        self.config.include('ptah')
        self.config.get_routes_mapper()
        self.registry = self.config.registry
        self.request.registry = self.registry

        #if self._init_auth:
        #    policy = AuthTktAuthenticationPolicy(
        #        'secret', callback= ptah.get_local_roles)

        #    self.registry.registerUtility(
        #        policy, IAuthenticationPolicy)

        #    self.registry.registerUtility(
        #        ACLAuthorizationPolicy(), IAuthorizationPolicy)

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
        import ptah.util
        ptah.util.tldata.clear()

        import ptah.security
        ptah.security.DEFAULT_ACL[:] = []

        from ptah.config import ATTACH_ATTR

        mod = sys.modules[self.__class__.__module__]
        if hasattr(mod, ATTACH_ATTR):
            delattr(mod, ATTACH_ATTR)

        testing.tearDown()
        transaction.abort()
