""" directives tests """
import unittest
from zope import interface
from zope.component import getSiteManager
from zope.configuration.config import ConfigurationConflictError
from zope.component.event import objectEventNotify
from martian.error import GrokImportError

from memphis import config


class BaseTesting(unittest.TestCase):

    def _init_memphis(self, settings={}, *args, **kw):
        config.loadPackage('memphis.config')
        config.begin()
        config.addPackage(self.__class__.__module__)
        config.commit()

    def setUp(self):
        sm = getSiteManager()
        sm.__init__('base')

    def tearDown(self):
        sm = getSiteManager()
        sm.__init__('base')

        config.cleanUp()
        
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

    def test_adapts(self):
        global TestClass

        class TestClass(object):
            config.adapts(IContext)
            config.adapts(IContext)
            interface.implements(IAdapter)

        self._init_memphis()

        sm = getSiteManager()
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][0] == '')
        self.assertTrue(adapters[0][1] is TestClass)

    def test_adapts_named(self):
        global TestClass

        class TestClass(object):
            config.adapts(IContext, name='test')
            interface.implements(IAdapter)

        self._init_memphis()

        sm = getSiteManager()
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is TestClass)

    def test_adapts_multiple(self):
        global TestClass

        class TestClass(object):
            config.adapts(IContext, IContext2)
            interface.implements(IAdapter)

        self._init_memphis()

        sm = getSiteManager()
        adapters = sm.adapters.lookupAll((IContext, IContext2), IAdapter)

        self.assertTrue(adapters[0][0] == '')
        self.assertTrue(adapters[0][1] is TestClass)

    def test_adapts_multiple_named(self):
        global TestClass

        class TestClass(object):
            config.adapts(IContext, IContext2, name='test')
            interface.implements(IAdapter)

        self._init_memphis()

        sm = getSiteManager()
        adapters = sm.adapters.lookupAll((IContext, IContext2), IAdapter)

        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is TestClass)

    def test_adapts_reinitialize(self):
        global TestClass

        class TestClass(object):
            config.adapts(IContext)
            interface.implements(IAdapter)

        self._init_memphis()

        # reinstall
        config.cleanUp()

        sm = getSiteManager()
        sm.__init__('base')
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)
        self.assertTrue(len(adapters) == 0)

        self._init_memphis()
        
        sm = getSiteManager()
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is TestClass)


class TestAdapterDirective(BaseTesting):

    def test_adapter(self):
        global testAdapter

        @config.adapter(IContext)
        @config.adapter(IContext2)
        @interface.implementer(IAdapter)
        def testAdapter(context):
            pass
        testAdapter(None) # coverage

        self._init_memphis()

        sm = getSiteManager()
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
        def testAdapter(context): pass
        testAdapter(None) # coverage

        self._init_memphis()

        sm = getSiteManager()
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is testAdapter)

    def test_adapter_multple(self):
        global testAdapter

        @config.adapter(IContext, IContext2, name='test')
        @interface.implementer(IAdapter)
        def testAdapter(context): pass
        testAdapter(None) # coverage

        self._init_memphis()

        sm = getSiteManager()
        adapters = sm.adapters.lookupAll((IContext, IContext2), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is testAdapter)

    def test_adapter_errs1(self):
        global testAdapter

        @config.adapter(IContext, name='test')
        def testAdapter(context): pass
        testAdapter(None) # coverage

        self.assertRaises(ValueError, self._init_memphis)

    def test_adapter_errs2(self):
        global testAdapter

        @config.adapter(IContext)
        @config.adapter(IContext)
        @interface.implementer(IAdapter)
        def testAdapter(context): pass
        testAdapter(None) # coverage

        self.assertRaises(ConfigurationConflictError, self._init_memphis)

    def test_adapter_reinitialize(self):
        global testAdapter

        @config.adapter(IContext)
        @config.adapter(IContext2)
        @interface.implementer(IAdapter)
        def testAdapter(context): pass
        testAdapter(None) # coverage

        self._init_memphis()

        # reinstall
        config.cleanUp()

        sm = getSiteManager()
        sm.__init__('base')

        self._init_memphis()

        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is testAdapter)

        adapters = sm.adapters.lookupAll((IContext2,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is testAdapter)


class TestUtilityDirective(BaseTesting):

    def test_utility(self):
        global TestClass
        try:
            e = None
            class TestClass(object):
                config.utility(IContext)
                config.utility(IContext)
        except Exception, e:
            pass

        self.assertTrue(isinstance(e, GrokImportError))

        class TestClass(object):
            config.utility(IContext)

        self._init_memphis()

        sm = getSiteManager()
        util = sm.getUtility(IContext)
        self.assertTrue(isinstance(util, TestClass))

    def test_utility_named(self):
        global TestClass
        class TestClass(object):
            config.utility(IContext, name='test')

        self._init_memphis()

        sm = getSiteManager()
        util = sm.getUtility(IContext, 'test')
        self.assertTrue(isinstance(util, TestClass))

        self.assertTrue(sm.queryUtility(IContext) is None)

    def test_utility_reinitialize(self):
        global TestClass
        class TestClass(object):
            config.utility(IContext)

        self._init_memphis()

        # reinstall
        config.cleanUp()

        sm = getSiteManager()
        sm.__init__('base')

        self._init_memphis()
        
        sm = getSiteManager()
        util = sm.getUtility(IContext)
        self.assertTrue(isinstance(util, TestClass))


class TestHandlerDirective(BaseTesting):

    def test_handler(self):
        global testHandler

        events = []

        @config.handler(IContext)
        def testHandler(*args):
            events.append(args)

        self._init_memphis()

        sm = getSiteManager()
        sm.subscribers((Context(IContext),), None)

        self.assertTrue(len(events) == 1)

        sm.subscribers((Context(IContext2),), None)
        self.assertTrue(len(events) == 1)

    def test_handler_several(self):
        global testHandler

        events = []

        @config.handler(IContext)
        @config.handler(IContext2)
        def testHandler(*args):
            events.append(args)

        self._init_memphis()

        sm = getSiteManager()
        sm.subscribers((Context(IContext),), None)
        sm.subscribers((Context(IContext2),), None)

        self.assertTrue(len(events) == 2)

    def test_handler_object(self):
        global testHandler
        from zope.component.interfaces import IObjectEvent, ObjectEvent

        events = []

        @config.handler(IContext, IObjectEvent)
        def testHandler(*args):
            events.append(args)

        self._init_memphis()
        
        sm = getSiteManager()
        sm.registerHandler(objectEventNotify)

        sm.subscribers((ObjectEvent(Context(IContext)),), None)

        self.assertTrue(len(events) == 1)
        self.assertTrue(len(events[0]) == 2)

    def test_handler_reinitialize(self):
        global testHandler

        events = []

        @config.handler(IContext)
        def testHandler(*args):
            events.append(args)

        self._init_memphis()

        # reinstall
        config.cleanUp()

        sm = getSiteManager()
        sm.__init__('base')

        self._init_memphis()

        sm = getSiteManager()
        sm.subscribers((Context(IContext),), None)
        self.assertTrue(len(events) == 1)
