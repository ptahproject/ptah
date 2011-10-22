import ptah
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound

from base import Base


class TestIntrospectModule(Base):

    def test_introspect_module(self):
        from ptah.manage.manage import PtahManageRoute
        from ptah.manage.introspect import IntrospectModule, Package

        request = DummyRequest()

        ptah.authService.set_userid('test')
        ptah.PTAH_CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['introspect']

        self.assertIsInstance(mod, IntrospectModule)

        self.assertRaises(KeyError, mod.__getitem__, 'unknown')

        package = mod['ptah']
        self.assertIsInstance(package, Package)

    def test_introspect_view(self):
        from ptah.manage.introspect import IntrospectModule, MainView

        request = DummyRequest()

        mod = IntrospectModule(None, request)

        res = MainView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')

        view = MainView(mod, request)
        view.update()

        self.assertTrue(bool(view.packages))

    def test_introspect_package_view(self):
        from ptah.manage.introspect import IntrospectModule, PackageView

        request = DummyRequest()

        mod = IntrospectModule(None, request)

        for pkg in mod.list_packages():
            package = mod[pkg]

            res = PackageView.__renderer__(package, request)
            self.assertEqual(res.status, '200 OK')

    def test_introspect_routes(self):
        from ptah.manage.introspect import IntrospectModule, RoutesView

        request = DummyRequest()

        mod = IntrospectModule(None, request)

        res = RoutesView.__renderer__(mod, request)
        self.assertIn("Routes <small>registered pyramid routes</small>",
                      res.body)

    def test_introspect_events(self):
        from ptah.manage.introspect import IntrospectModule, EventsView

        request = DummyRequest()
        mod = IntrospectModule(None, request)
        res = EventsView.__renderer__(mod, request)

        self.assertIn("Events <small>event declarations</small>", res.body)

    def test_introspect_events_event(self):
        from ptah.manage.introspect import IntrospectModule, EventsView

        request = DummyRequest(
            params = {'ev': 'ptah.config.settings.SettingsInitialized'})
        mod = IntrospectModule(None, request)
        res = EventsView.__renderer__(mod, request)

        self.assertIn("Event: Settings initialized event", res.body)

    def test_introspect_source(self):
        from ptah.manage.introspect import IntrospectModule, SourceView

        request = DummyRequest()
        mod = IntrospectModule(None, request)
        res = SourceView.__renderer__(mod, request)
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')

    def test_introspect_source_view(self):
        from ptah.manage.introspect import IntrospectModule, SourceView

        request = DummyRequest(
            params = {'pkg': 'ptah.view.customize'})
        
        mod = IntrospectModule(None, request)
        res = SourceView.__renderer__(mod, request)
        self.assertIn('Source: ptah/customize.py', res.body)


class TestUriView(Base):

    def setUp(self):
        self._setup_pyramid()

    def test_uri_view(self):
        from ptah.manage.introspect import IntrospectModule, UriResolver

        request = DummyRequest(
            GET = {'uri': 'ptah+auth:superuser'})
        mod = IntrospectModule(None, request)

        view = UriResolver(mod, request)
        view.update()

        self.assertEqual(view.data[0]['name'],
                         'ptah.authentication.superuser_resolver')

    def test_uri_handler(self):
        from ptah.manage.introspect import IntrospectModule, UriResolver

        request = DummyRequest(
            POST = {'form.buttons.show': 'Show'})
        mod = IntrospectModule(None, request)

        view = UriResolver(mod, request)
        view.update()

        request = DummyRequest(
            POST = {'form.buttons.show': 'Show', 'uri': 'ptah+auth:superuser'})
        mod = IntrospectModule(None, request)

        view = UriResolver(mod, request)
        view.update()

        self.assertEqual(view.data[0]['name'],
                         'ptah.authentication.superuser_resolver')
