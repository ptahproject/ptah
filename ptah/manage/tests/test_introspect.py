import ptah
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest


class TestIntrospectModule(PtahTestCase):

    _init_ptah = False

    def test_introspect_module(self):
        self.init_ptah()

        from ptah.manage.manage import PtahManageRoute
        from ptah.manage.introspect import IntrospectModule, Package

        request = DummyRequest()

        ptah.auth_service.set_userid('test')
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['managers'] = ('*',)
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

        self.config.add_route('test-route', '/test/')

        self.init_ptah()

        request = DummyRequest()

        mod = IntrospectModule(None, request)
        res = RoutesView.__renderer__(mod, request)

        self.assertIn(
            "Routes <small>registered pyramid routes</small>", res.text)
        self.assertIn('/test/', res.text)
        self.assertIn('/test/introspect', res.text)
        self.assertIn('Route view', res.text)

    def test_introspect_events(self):
        from ptah.manage import introspect
        from ptah.manage.introspect import IntrospectModule, EventsView

        introspect.exclude = None

        global TestEvent, eventHandler1, eventHandler2

        @ptah.event('Test event')
        class TestEvent(object):
            pass

        @ptah.subscriber(TestEvent)
        def eventHandler1(ev):
            """ """

        @ptah.subscriber(None, TestEvent)
        def eventHandler2(context, ev):
            """ """

        self.init_ptah()

        request = DummyRequest()
        mod = IntrospectModule(None, request)
        res = EventsView.__renderer__(mod, request)

        self.assertIn("Events <small>event declarations</small>", res.text)
        self.assertIn("Test event", res.text)

        request = DummyRequest(
            params={'ev': 'ptah.manage.tests.test_introspect.TestEvent'})
        res = EventsView.__renderer__(mod, request)

        self.assertIn('Event: Test event', res.text)
        #self.assertIn('eventHandler1', res.text)
        #self.assertIn('eventHandler2', res.text)


class TestSubscriberIntrospect(PtahTestCase):

    def test_introspect_subscriber_introspect(self):
        from ptah import config
        from ptah.manage.introspect import SubscriberDirective

        @ptah.subscriber(TestEvent)
        def eventHandler1(ev):
            """ """

        @ptah.subscriber(None, TestEvent)
        def eventHandler2(context, ev):
            """ """

        data = config.scan(self.__class__.__module__, set())

        actions = []
        for action in data:
            if action.discriminator[0] == 'ptah.config:subscriber':
                actions.append(action)

        ti = SubscriberDirective(self.request)
        res = ti.renderActions(*actions)

        self.assertIn('ptah.manage.tests.test_introspect.eventHandler1', res)
        self.assertIn('ptah.manage.tests.test_introspect.eventHandler2', res)


class TestRouteIntrospect(PtahTestCase):

    def test_introspect_route_introspect(self):
        from ptah import config
        from ptah.manage.introspect import RouteDirective

        ptah.view.register_route('test-introspect', '/test/introspect')
        data = config.scan(self.__class__.__module__, set())

        actions = []
        for action in data:
            if action.discriminator[0] == 'ptah.view:route':
                actions.append(action)

        ti = RouteDirective(self.request)
        res = ti.renderActions(*actions)

        self.assertIn('test-introspect: /test/introspect', res)


class TestViewIntrospect(PtahTestCase):

    def test_introspect_view_introspect(self):
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

        data = ptah.config.scan(self.__class__.__module__, set())

        actions = []
        for action in data:
            if action.discriminator[0] == 'ptah.view:view':
                actions.append(action)

        ti = ViewDirective(self.request)
        res = ti.renderActions(*actions)

        self.assertIn('route: "test-introspect"', res)
        self.assertIn('view: "view2.html" route: "test-introspect"', res)
        self.assertIn('view: view3.html', res)
