import ptah
from pyramid.testing import DummyRequest

from base import Base

class TestEvent(object):
    ptah.config.event('Test event')

@ptah.config.subscriber(TestEvent)
@ptah.config.subscriber(TestEvent, TestEvent)
def eventHandler(ev):
    """ """

ptah.view.register_route('test-introspect', '/test/introspect')


class TestIntrospectModule(Base):

    def tearDown(self):
        ptah.config.cleanup_system(self.__class__.__module__)
        super(TestIntrospectModule, self).tearDown()

    def test_introspect_module(self):
        from ptah.manage.manage import CONFIG, PtahManageRoute
        from ptah.manage.introspect import IntrospectModule, Package

        request = DummyRequest()

        ptah.authService.set_userid('test')
        CONFIG['managers'] = ('*',)
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

        self.p_config.add_route('test-route', '/test/')

        request = DummyRequest()

        mod = IntrospectModule(None, request)

        res = RoutesView.__renderer__(mod, request)

        self.assertIn(
            "Routes <small>registered pyramid routes</small>", res.body)

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
