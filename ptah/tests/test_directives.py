""" directives tests """
import sys
from pyramid import testing

from zope import interface
from zope.interface.interfaces import IObjectEvent

from ptah import config
from ptah.testing import TestCase


class BaseTesting(TestCase):

    def _init_ptah(self, *args, **kw):
        self.config.include('ptah')
        self.config.scan(self.__class__.__module__)
        self.config.commit()
        self.config.autocommit = True

    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config.include('ptah')
        self.registry = self.config.registry

    def tearDown(self):
        mod = sys.modules[self.__class__.__module__]
        if hasattr(mod, config.ATTACH_ATTR):
            delattr(mod, config.ATTACH_ATTR)

        testing.tearDown()


class IContext(interface.Interface):
    pass


class IContext2(interface.Interface):
    pass


class Context(object):

    def __init__(self, iface):
        interface.directlyProvides(self, iface)


class TestSubscriberDirective(BaseTesting):

    def test_subscriber(self):
        events = []

        @config.subscriber(IContext)
        def testHandler(*args):
            events.append(args)

        self._init_ptah()

        sm = self.registry
        sm.subscribers((Context(IContext),), None)

        self.assertTrue(len(events) == 1)

        sm.subscribers((Context(IContext2),), None)
        self.assertTrue(len(events) == 1)

    def test_subscriber_multple(self):
        events = []

        @config.subscriber(IContext)
        @config.subscriber(IContext2)
        def testHandler(*args):
            events.append(args)

        self._init_ptah()

        sm = self.registry
        sm.subscribers((Context(IContext),), None)
        sm.subscribers((Context(IContext2),), None)

        self.assertTrue(len(events) == 2)

    def test_subscriber_object(self):
        from zope.interface.interfaces import ObjectEvent

        events = []

        @config.subscriber(IContext, IObjectEvent)
        def testSubscriber(*args):
            events.append(args)

        self._init_ptah()

        sm = self.config.registry
        sm.subscribers((ObjectEvent(Context(IContext)),), None)

        self.assertTrue(len(events) == 1)
        self.assertTrue(len(events[0]) == 2)


class TestExtraDirective(BaseTesting):

    def test_action(self):
        info = config.DirectiveInfo(0)

        action = config.Action(None, discriminator=('test', ))

        self.assertIsNone(action.hash)

        info.attach(action)

        self.assertIsNotNone(action.hash)
        self.assertIsNotNone(hash(action))
        self.assertRaises(TypeError, info.attach, action)
        self.assertEqual('<Action "test">', repr(action))
        self.assertIn('test_action\n', repr(info), '')
