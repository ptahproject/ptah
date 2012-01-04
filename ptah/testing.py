""" base class """
import sys
import sqlalchemy
import transaction
import pkg_resources
from zope.interface import directlyProvides
from pyramid import testing
from pyramid.interfaces import \
     IRequest, IAuthenticationPolicy, IAuthorizationPolicy
from pyramid.interfaces import IRouteRequest
from pyramid.view import render_view, render_view_to_response
from pyramid.path import package_name
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy

if sys.version_info[:2] == (2, 6): # pragma: no cover
    from unittest2 import TestCase
else:
    from unittest import TestCase

import ptah
from ptah import config


class PtahTestCase(TestCase):

    _init_ptah = True
    _init_sqla = True

    _settings = {'sqlalchemy.url': 'sqlite://'}
    _packages = ()
    _trusted_manage = True
    _environ = {
        'wsgi.url_scheme':'http',
        'wsgi.version':(1,0),
        'HTTP_HOST': 'example.com',
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
        self.config.include('ptah')

        pkg = package_name(sys.modules[self.__class__.__module__])
        if pkg != 'ptah':
            packages = []
            parts = self.__class__.__module__.split('.')
            for l in range(len(parts)):
                pkg = '.'.join(parts[:l+1])
                if pkg == 'ptah' or pkg.startswith('ptah.'):
                    continue
                try: # pragma: no cover
                    self.config.include(pkg)
                except: # pragma: no cover
                    pass

        self.config.commit()
        self.config.autocommit = True

        self.config.ptah_init_settings()

        ptah.reset_session()

        if self._init_sqla:
            # create engine
            self.config.ptah_init_sql()

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

    def render_route_view(self, context, request, route_name, view=''): # pragma: no cover
        directlyProvides(
            request, self.registry.getUtility(IRouteRequest, route_name))

        return render_view_to_response(context, request, view)
