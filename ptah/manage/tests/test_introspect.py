import ptah
from pyramid.testing import DummyRequest

from base import Base


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
        from ptah.manage import introspect
        from ptah.manage.introspect import IntrospectModule, RoutesView

        introspect.exclude = None

        ptah.view.register_route('test-introspect', '/test/introspect')

        global view

        @ptah.view.pview(route='test-introspect')
        def view(request):
            """ """

        self.p_config.add_route('test-route', '/test/')

        self._init_ptah()

        request = DummyRequest()

        mod = IntrospectModule(None, request)
        res = RoutesView.__renderer__(mod, request)

        self.assertIn(
            "Routes <small>registered pyramid routes</small>", res.body)
        self.assertIn('/test/', res.body)
        self.assertIn('/test/introspect', res.body)
        self.assertIn('Route view', res.body)

    def test_introspect_events(self):
        from ptah.manage import introspect
        from ptah.manage.introspect import IntrospectModule, EventsView

        introspect.exclude = None

        global TestEvent, eventHandler1, eventHandler2

        class TestEvent(object):
            ptah.config.event('Test event')

        @ptah.config.subscriber(TestEvent)
        def eventHandler1(ev):
            """ """

        @ptah.config.subscriber(None, TestEvent)
        def eventHandler2(context, ev):
            """ """

        self._init_ptah()

        request = DummyRequest()
        mod = IntrospectModule(None, request)
        res = EventsView.__renderer__(mod, request)

        self.assertIn("Events <small>event declarations</small>", res.body)
        self.assertIn("Test event", res.body)

        request = DummyRequest(
            params={'ev': 'ptah.manage.tests.test_introspect.TestEvent'})
        res = EventsView.__renderer__(mod, request)

        self.assertIn('Event: Test event', res.body)
        self.assertIn('eventHandler1', res.body)
        self.assertIn('eventHandler2', res.body)


class TestSubscriberIntrospect(Base):

    def test_introspect_subscriber_introspect(self):
        from ptah.config import directives
        from ptah.manage.introspect import SubscriberDirective

        @ptah.config.subscriber(TestEvent)
        def eventHandler1(ev):
            """ """

        @ptah.config.subscriber(None, TestEvent)
        def eventHandler2(context, ev):
            """ """

        data = directives.scan(self.__class__.__module__, set())

        actions = []
        for action in data:
            if action.discriminator[0] == 'ptah.config:subscriber':
                actions.append(action)

        ti = SubscriberDirective(self.request)
        res = ti.renderActions(*actions)

        self.assertIn('ptah.manage.tests.test_introspect.eventHandler1', res)
        self.assertIn('ptah.manage.tests.test_introspect.eventHandler2', res)


class TestRouteIntrospect(Base):

    def test_introspect_route_introspect(self):
        from ptah.config import directives
        from ptah.manage.introspect import RouteDirective

        ptah.view.register_route('test-introspect', '/test/introspect')
        data = directives.scan(self.__class__.__module__, set())

        actions = []
        for action in data:
            if action.discriminator[0] == 'ptah.view:route':
                actions.append(action)

        ti = RouteDirective(self.request)
        res = ti.renderActions(*actions)

        self.assertIn('test-introspect: /test/introspect', res)


class TestViewIntrospect(Base):

    def test_introspect_view_introspect(self):
        from ptah.config import directives
        from ptah.manage.introspect import ViewDirective

        ptah.view.register_route('test-introspect', '/test/introspect')

        global view1, view2, view3

        @ptah.view.pview(route='test-introspect')
        def view1(request):
            """ """

        @ptah.view.pview('view2.html', route='test-introspect')
        def view2(request):
            """ """

        class view3(ptah.view.View):
            ptah.view.pview('view3.html')

        data = directives.scan(self.__class__.__module__, set())

        actions = []
        for action in data:
            if action.discriminator[0] == 'ptah.view:view':
                actions.append(action)

        ti = ViewDirective(self.request)
        res = ti.renderActions(*actions)

        self.assertIn('route: "test-introspect"', res)
        self.assertIn('view: "view2.html" route: "test-introspect"', res)
        self.assertIn('view: view3.html', res)
