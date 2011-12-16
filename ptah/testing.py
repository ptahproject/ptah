""" base class """
import sys
import unittest
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

    _settings = {'sqlalchemy.url': 'sqlite://'}
    _packages = ()
    _trusted_manage = True
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
            # create engine
            ptah.reset_session()
            self.config.ptah_initialize_sql()

            # create sql tables
            Base = ptah.get_base()
            Base.metadata.create_all()
            transaction.commit()

        if self._trusted_manage:
            def trusted(*args):
                return True
            ptah.manage.set_access_manager(trusted)

    def init_pyramid(self):
        self.request = request = self.make_request()
        self.config = testing.setUp(
            request=request, settings=self._settings, autocommit=False)
        self.config.include('ptah')
        self.config.get_routes_mapper()
        self.registry = self.config.registry
        self.request.registry = self.registry

    def setUp(self):
        ptah.QueryFreezer._testing = True
        self.init_pyramid()

        if self._init_ptah:
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
