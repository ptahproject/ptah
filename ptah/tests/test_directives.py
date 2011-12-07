""" directives tests """
import sys
import unittest
from pyramid import testing
from pyramid.exceptions import ConfigurationConflictError

from zope import interface
from zope.interface.registry import Components
from zope.interface.interfaces import IObjectEvent

import ptah
from ptah import config


class BaseTesting(unittest.TestCase):

    def _init_ptah(self, settings={}, pconfig=None, *args, **kw):
        if pconfig is None:
            pconfig = self.config
        ptah.config.initialize(
            pconfig, ('ptah.config', 'ptah.events', self.__class__.__module__))
        self.config.commit()
        self.config.autocommit = True

    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config.include('ptah')
        self.registry = self.config.registry

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)

        global TestClass, testAdapter, testHandler
        try:
            del TestClass
        except:
            pass
        try:
            del testAdapter
        except:
            pass
        try:
            del testHandler
        except:
            pass

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
        global TestClass

        @interface.implementer(IAdapter)
        class TestClass(object):
            config.adapter(IContext)
            config.adapter(IContext)

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
        global TestClass

        @interface.implementer(IAdapter)
        class TestClass(object):
            config.adapter(IContext)

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
        global TestClass

        @interface.implementer(IAdapter)
        class TestClass(object):
            config.adapter(IContext, name='test')

        self._init_ptah()

        sm = self.registry
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is TestClass)

    def test_adapts_multiple(self):
        global TestClass

        @interface.implementer(IAdapter)
        class TestClass(object):
            config.adapter(IContext, IContext2)

        self._init_ptah()

        sm = self.registry
        adapters = sm.adapters.lookupAll((IContext, IContext2), IAdapter)

        self.assertTrue(adapters[0][0] == '')
        self.assertTrue(adapters[0][1] is TestClass)

    def test_adapts_multiple_named(self):
        global TestClass

        @interface.implementer(IAdapter)
        class TestClass(object):
            config.adapter(IContext, IContext2, name='test')

        self._init_ptah()

        sm = self.registry
        adapters = sm.adapters.lookupAll((IContext, IContext2), IAdapter)

        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is TestClass)

    def test_adapts_reinitialize(self):
        global TestClass

        @interface.implementer(IAdapter)
        class TestClass(object):
            config.adapter(IContext)

        self._init_ptah()

        # reinstall
        config.cleanup_system()

        sm = self.registry
        sm.__init__('base')
        sm.__ptah_storage__.clear()

        adapters = sm.adapters.lookupAll((IContext,), IAdapter)
        self.assertTrue(len(adapters) == 0)

        self._init_ptah()

        sm = self.registry
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is TestClass)


class TestAdapterDirective(BaseTesting):

    def test_adapter(self):
        global testAdapter

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
        global testAdapter

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
        global testAdapter

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
        global testAdapter

        err = None
        try:
            @config.adapter(IContext, name='test')
            def testAdapter(context):  # pragma: no cover
                pass
        except Exception as e:
            err = e

        self.assertTrue(isinstance(err, TypeError))

    def test_adapter_errs2(self):
        global testAdapter

        @config.adapter(IContext)
        @config.adapter(IContext)
        @interface.implementer(IAdapter)
        def testAdapter(context):  # pragma: no cover
            pass

        self.assertRaises(ConfigurationConflictError, self._init_ptah)

    def test_adapter_reinitialize(self):
        global testAdapter

        @config.adapter(IContext)
        @config.adapter(IContext2)
        @interface.implementer(IAdapter)
        def testAdapter(context):  # pragma: no cover
            pass

        self._init_ptah()

        # reinstall
        config.cleanup_system()

        sm = self.registry
        sm.__init__('base')
        sm.__ptah_storage__.clear()

        self._init_ptah()

        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is testAdapter)

        adapters = sm.adapters.lookupAll((IContext2,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is testAdapter)


class TestSubscriberDirective(BaseTesting):

    def test_subscriber(self):
        global testSubscriber

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
        global testSubscriber

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
        global testSubscriber
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

    def test_subscriber_reinitialize(self):
        global testSubscriber

        events = []

        @config.subscriber(IContext)
        def testSubscriber(*args):
            events.append(args)

        self._init_ptah()

        # reinstall
        config.cleanup_system()

        sm = self.registry
        sm.__init__('base')
        sm.__ptah_storage__.clear()

        self._init_ptah()

        sm = self.registry
        sm.subscribers((Context(IContext),), None)
        self.assertTrue(len(events) == 1)


class TestExtraDirective(BaseTesting):

    def test_scan_unknown(self):
        self.assertRaises(ImportError,  config.scan, 'unknown', [])

    def test_directive_info_limit_scope(self):
        self.assertRaises(
            TypeError,
            config.DirectiveInfo, 2, allowed_scope=('class',))

    def test_directive_info_context(self):
        info = config.DirectiveInfo(0)
        info.scope = 'module'

        self.assertEqual(info.module,
                         sys.modules[self.__class__.__module__])
        self.assertEqual(info.context,
                         sys.modules[self.__class__.__module__])

    def test_api_loadpackage(self):
        from ptah import config

        seen = set()
        packages = config.load_package('ptah.config', seen)
        self.assertEqual(packages, ['ptah.config'])

        packages = config.load_package('ptah.config', seen)
        self.assertEqual(packages, [])

    def test_action(self):
        info = config.DirectiveInfo()

        action = config.Action(None, discriminator=('test', ))

        self.assertIsNone(action.hash)

        info.attach(action)

        self.assertIsNotNone(action.hash)
        self.assertIsNotNone(hash(action))
        self.assertRaises(TypeError, info.attach, action)
        self.assertEqual(repr(action), '<Action "test">')
