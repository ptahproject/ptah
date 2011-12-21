import ptah
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest


class _TestIntrospectModule(PtahTestCase):

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


class _TestSubscriberIntrospect(PtahTestCase):

    def _test_introspect_subscriber_introspect(self):
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
