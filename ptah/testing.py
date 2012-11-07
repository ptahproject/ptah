""" base class """
import sys
import transaction
from zope.interface import directlyProvides
from pyramid import testing
from pyramid.interfaces import IRequest
from pyramid.interfaces import IRouteRequest
from pyramid.interfaces import IRequestExtensions
from pyramid.view import render_view_to_response
from pyramid.path import package_name
from player.renderer import render

if sys.version_info[:2] == (2, 6): # pragma: no cover
    import unittest2 as unittest
    from unittest2 import TestCase
else:
    import unittest
    from unittest import TestCase

import ptah


class PtahTestCase(TestCase):

    _init_ptah = True
    _init_sqla = True
    _includes = ()
    _auto_commit = True

    _settings = {'sqlalchemy.url': 'sqlite://'}
    _packages = ()
    _trusted_manage = True
    _environ = {
        'wsgi.url_scheme':'http',
        'wsgi.version':(1,0),
        'HTTP_HOST': 'example.com',
        'SCRIPT_NAME': '',
        'PATH_INFO': '/',}

    def make_request(self, registry=None, environ=None,
                     request_iface=IRequest, **kwargs):
        if registry is None:
            registry = self.registry
        if environ is None:
            environ=self._environ
        request = testing.DummyRequest(environ=environ, **kwargs)
        request.request_iface = IRequest
        request.registry = registry
        request._set_extensions(registry.getUtility(IRequestExtensions))
        return request

    def init_request_extensions(self, registry):
        from pyramid.config.factories import _RequestExtensions

        exts = registry.queryUtility(IRequestExtensions)
        if exts is None:
            exts = _RequestExtensions()
            registry.registerUtility(exts, IRequestExtensions)

    def init_ptah(self, *args, **kw):
        self.registry.settings.update(self._settings)
        self.config.include('ptah')

        for pkg in self._includes: # pragma: no cover
            self.config.include(pkg)

        pkg = package_name(sys.modules[self.__class__.__module__])
        if pkg != 'ptah':
            parts = self.__class__.__module__.split('.')
            for l in range(len(parts)):
                pkg = '.'.join(parts[:l+1])
                if pkg == 'ptah' or pkg.startswith('ptah.') or \
                       pkg in self._includes:
                    continue # pragma: no cover
                try:
                    self.config.include(pkg)
                except: # pragma: no cover
                    pass

        self.config.scan(self.__class__.__module__)

        self.config.commit()
        self.config.autocommit = self._auto_commit

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
        self.config = testing.setUp(settings=self._settings, autocommit=False)
        self.config.get_routes_mapper()
        self.init_request_extensions(self.config.registry)
        self.registry = self.config.registry

        self.config.include('pform')
        self.config.include('player')
        self.config.include('pyramid_amdjs')

        self.request = self.make_request()
        def set_ext():
            self.request._set_extensions(
                self.registry.getUtility(IRequestExtensions))

        self.config.action(id(self), callable=set_ext)
        self.config.begin(self.request)

    def setUp(self):
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
