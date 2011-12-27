""" directives tests """
import sys
from pyramid import testing
from pyramid.exceptions import ConfigurationConflictError

from zope import interface
from zope.interface.registry import Components
from zope.interface.interfaces import IObjectEvent

import ptah
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


class IAdapter(interface.Interface):
    pass


class Context(object):

    def __init__(self, iface):
        interface.directlyProvides(self, iface)


class TestAdaptsDirective(BaseTesting):

    def test_adapts_err(self):
        @ptah.adapter(IContext)
        @ptah.adapter(IContext)
        @interface.implementer(IAdapter)
        class TestClass(object):
            """ """

        err = None
        try:
            self._init_ptah()
        except Exception as e:
            err = e

        s = str(err)
        self.assertTrue(isinstance(err, ConfigurationConflictError))
        self.assertTrue('ptah.config:adapter' in s)
        self.assertTrue('test_directives' in s)

    def test_adapts(self):
        @ptah.adapter(IContext)
        @interface.implementer(IAdapter)
        class TestClass(object):
            def __init__(self, context):
                pass

        self._init_ptah()

        sm = self.registry
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][0] == '')
        self.assertTrue(adapters[0][1] is TestClass)

        adapter = sm.getAdapter(Context(IContext), IAdapter)
        self.assertTrue(isinstance(adapter, TestClass))

    def test_adapts_named(self):
        @ptah.adapter(IContext, name='test')
        @interface.implementer(IAdapter)
        class TestClass(object):
            """ """

        self._init_ptah()

        sm = self.registry
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is TestClass)

    def test_adapts_multiple(self):
        @ptah.adapter(IContext, IContext2)
        @interface.implementer(IAdapter)
        class TestClass(object):
            """ """
        self._init_ptah()

        sm = self.registry
        adapters = sm.adapters.lookupAll((IContext, IContext2), IAdapter)

        self.assertTrue(adapters[0][0] == '')
        self.assertTrue(adapters[0][1] is TestClass)

    def test_adapts_multiple_named(self):
        @ptah.adapter(IContext, IContext2, name='test')
        @interface.implementer(IAdapter)
        class TestClass(object):
            """ """
        self._init_ptah()

        sm = self.registry
        adapters = sm.adapters.lookupAll((IContext, IContext2), IAdapter)

        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is TestClass)

    def test_adapts_reinitialize(self):
        @ptah.adapter(IContext)
        @interface.implementer(IAdapter)
        class TestClass(object):
            """ """

        self._init_ptah()

        # reinstall
        sm = self.registry
        sm.__init__('base')

        adapters = sm.adapters.lookupAll((IContext,), IAdapter)
        self.assertTrue(len(adapters) == 0)

        self._init_ptah()

        sm = self.registry
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is TestClass)


class TestAdapterDirective(BaseTesting):

    def test_adapter(self):
        @config.adapter(IContext)
        @config.adapter(IContext2)
        @interface.implementer(IAdapter)
        def testAdapter(context):  # pragma: no cover
            pass

        self._init_ptah()

        sm = self.registry
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is testAdapter)

        adapters = sm.adapters.lookupAll((IContext2,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is testAdapter)

    def test_adapter_named(self):
        @config.adapter(IContext, name='test')
        @interface.implementer(IAdapter)
        def testAdapter(context):  # pragma: no cover
            pass

        self._init_ptah()

        sm = self.registry
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is testAdapter)

    def test_adapter_multple(self):
        @config.adapter(IContext, IContext2, name='test')
        @interface.implementer(IAdapter)
        def testAdapter(context):  # pragma: no cover
            pass

        self._init_ptah()

        sm = self.registry
        adapters = sm.adapters.lookupAll((IContext, IContext2), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is testAdapter)

    def test_adapter_errs1(self):
        err = None
        try:
            @config.adapter(IContext, name='test')
            def testAdapter(context):  # pragma: no cover
                pass
        except Exception as e:
            err = e

        self.assertTrue(isinstance(err, TypeError))

    def test_adapter_errs2(self):
        @config.adapter(IContext)
        @config.adapter(IContext)
        @interface.implementer(IAdapter)
        def testAdapter(context):  # pragma: no cover
            pass

        self.assertRaises(ConfigurationConflictError, self._init_ptah)

    def test_adapter_reinitialize(self):
        @config.adapter(IContext)
        @config.adapter(IContext2)
        @interface.implementer(IAdapter)
        def testAdapter(context):  # pragma: no cover
            pass

        self._init_ptah()

        # reinstall
        sm = self.registry
        sm.__init__('base')

        self._init_ptah()

        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is testAdapter)

        adapters = sm.adapters.lookupAll((IContext2,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is testAdapter)


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
        from zope.interface.interfaces import IObjectEvent, ObjectEvent

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
        info = config.DirectiveInfo()

        action = config.Action(None, discriminator=('test', ))

        self.assertIsNone(action.hash)

        info.attach(action)

        self.assertIsNotNone(action.hash)
        self.assertIsNotNone(hash(action))
        self.assertRaises(TypeError, info.attach, action)
        self.assertEqual(repr(action), '<Action "test">')
