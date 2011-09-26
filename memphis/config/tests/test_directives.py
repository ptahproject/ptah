""" directives tests """
import sys, unittest
from zope import interface
from zope.interface.registry import Components
from zope.interface.interfaces import IObjectEvent

from memphis import config
from memphis.config import directives
from memphis.config.api import objectEventNotify


class BaseTesting(unittest.TestCase):

    def _init_memphis(self, settings={}, newReg=None, *args, **kw):
        config.initialize(('memphis.config', self.__class__.__module__),
                          reg=newReg)

    def tearDown(self):
        config.cleanUp(self.__class__.__module__)
        
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

    def test_adapts_err(self):
        global TestClass

        class TestClass(object):
            config.adapter(IContext)
            config.adapter(IContext)
            interface.implements(IAdapter)

        try:
            self._init_memphis()
        except Exception, e:
            pass

        s = str(e)
        self.assertTrue(isinstance(e, config.ConflictError))
        self.assertTrue('memphis.config:adapter' in s)
        self.assertTrue('test_directives.py' in s)

    def test_adapts(self):
        global TestClass

        class TestClass(object):
            config.adapter(IContext)
            interface.implements(IAdapter)

            def __init__(self, context):
                pass

        self._init_memphis()

        sm = config.registry
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][0] == '')
        self.assertTrue(adapters[0][1] is TestClass)

        adapter = IAdapter(Context(IContext))
        self.assertTrue(isinstance(adapter, TestClass))

    def test_adapts_named(self):
        global TestClass

        class TestClass(object):
            config.adapter(IContext, name='test')
            interface.implements(IAdapter)

        self._init_memphis()

        sm = config.registry
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is TestClass)

    def test_adapts_multiple(self):
        global TestClass

        class TestClass(object):
            config.adapter(IContext, IContext2)
            interface.implements(IAdapter)

        self._init_memphis()

        sm = config.registry
        adapters = sm.adapters.lookupAll((IContext, IContext2), IAdapter)

        self.assertTrue(adapters[0][0] == '')
        self.assertTrue(adapters[0][1] is TestClass)

    def test_adapts_multiple_named(self):
        global TestClass

        class TestClass(object):
            config.adapter(IContext, IContext2, name='test')
            interface.implements(IAdapter)

        self._init_memphis()

        sm = config.registry
        adapters = sm.adapters.lookupAll((IContext, IContext2), IAdapter)

        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is TestClass)

    def test_adapts_reinitialize(self):
        global TestClass

        class TestClass(object):
            config.adapter(IContext)
            interface.implements(IAdapter)

        self._init_memphis()

        # reinstall
        config.cleanUp()

        sm = config.registry
        sm.__init__('base')
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)
        self.assertTrue(len(adapters) == 0)

        self._init_memphis()
        
        sm = config.registry
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is TestClass)


class TestAdapterDirective(BaseTesting):

    def test_adapter(self):
        global testAdapter

        @config.adapter(IContext)
        @config.adapter(IContext2)
        @interface.implementer(IAdapter)
        def testAdapter(context): # pragma: no cover
            pass

        self._init_memphis()

        sm = config.registry
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
        def testAdapter(context): # pragma: no cover
            pass

        self._init_memphis()

        sm = config.registry
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is testAdapter)

    def test_adapter_multple(self):
        global testAdapter

        @config.adapter(IContext, IContext2, name='test')
        @interface.implementer(IAdapter)
        def testAdapter(context): # pragma: no cover
            pass

        self._init_memphis()

        sm = config.registry
        adapters = sm.adapters.lookupAll((IContext, IContext2), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][0] == 'test')
        self.assertTrue(adapters[0][1] is testAdapter)

    def test_adapter_errs1(self):
        global testAdapter

        try:
            @config.adapter(IContext, name='test')
            def testAdapter(context): # pragma: no cover
                pass
        except Exception, e:
            pass

        self.assertTrue(isinstance(e, TypeError))

    def test_adapter_errs2(self):
        global testAdapter

        @config.adapter(IContext)
        @config.adapter(IContext)
        @interface.implementer(IAdapter)
        def testAdapter(context):  # pragma: no cover
            pass

        self.assertRaises(config.ConflictError, self._init_memphis)

    def test_adapter_reinitialize(self):
        global testAdapter

        @config.adapter(IContext)
        @config.adapter(IContext2)
        @interface.implementer(IAdapter)
        def testAdapter(context): # pragma: no cover
            pass

        self._init_memphis()

        # reinstall
        config.cleanUp()

        sm = config.registry
        sm.__init__('base')

        self._init_memphis(newReg=config.registry)

        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is testAdapter)

        adapters = sm.adapters.lookupAll((IContext2,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is testAdapter)


class TestUtilityDirective(BaseTesting):

    def test_utility_err(self):
        global TestClass

        class TestClass(object):
            config.utility(IContext)
            config.utility(IContext)

        self.assertRaises(
            config.ConflictError, self._init_memphis)

    def test_utility_err2(self):
        global TestClass

        class TestClass(object):
            config.utility()

        self.assertRaises(
            TypeError, self._init_memphis)

    def test_utility(self):
        global TestClass

        class TestClass(object):
            config.utility(IContext)

        self._init_memphis()

        sm = config.registry
        util = sm.getUtility(IContext)
        self.assertTrue(isinstance(util, TestClass))

    def test_utility_default_interface(self):
        global TestClass

        class TestClass(object):
            interface.implements(IContext)
            config.utility()

        self._init_memphis()

        sm = config.registry
        util = sm.getUtility(IContext)
        self.assertTrue(isinstance(util, TestClass))

    def test_utility_named(self):
        global TestClass
        class TestClass(object):
            config.utility(IContext, name='test')

        self._init_memphis()

        sm = config.registry
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

        sm = config.registry
        sm.__init__('base')

        self._init_memphis()
        
        sm = config.registry
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

        sm = config.registry
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

        sm = config.registry
        sm.subscribers((Context(IContext),), None)
        sm.subscribers((Context(IContext2),), None)

        self.assertTrue(len(events) == 2)

    def test_handler_object(self):
        global testHandler
        from zope.interface.interfaces import IObjectEvent, ObjectEvent

        events = []

        @config.handler(IContext, IObjectEvent)
        def testHandler(*args):
            events.append(args)

        self._init_memphis()
        
        sm = config.registry
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

        sm = config.registry
        sm.__init__('base')

        self._init_memphis()

        sm = config.registry
        sm.subscribers((Context(IContext),), None)
        self.assertTrue(len(events) == 1)


class TestExtraDirective(BaseTesting):

    def test_scan_unknown(self):
        self.assertRaises(ImportError,  directives.scan, 'unknown', [])

    def test_scan_package(self):
        global testHandler

        @config.action
        def testHandler(*args): # pragma: no cover
            pass

        seen = set()
        actions = directives.scan(self.__class__.__module__, seen)
        
        self.assertTrue(len(actions) == 1)
        self.assertTrue(self.__class__.__module__ in seen)

        # already seen
        actions = directives.scan(self.__class__.__module__, seen)
        self.assertTrue(len(actions) == 0)

    def test_directive_info_limit_scope(self):
        self.assertRaises(
            TypeError, 
            directives.DirectiveInfo, 2, allowed_scope=('class',))

    def test_directive_info_context(self):
        info = directives.DirectiveInfo(0)
        info.scope = 'module'

        self.assertEqual(info.module, 
                         sys.modules[self.__class__.__module__])
        self.assertEqual(info.context, 
                         sys.modules[self.__class__.__module__])

    def test_api_init(self):
        global testHandler

        processed = []

        @config.action
        def testHandler(*args): # pragma: no cover
            processed.append(1)

        config.initialize()
        
        self.assertTrue(len(processed) == 0)

        config.initialize((self.__class__.__module__,))

        self.assertTrue(len(processed) == 1)

    def test_api_loadpackage(self):
        from memphis.config import api

        seen = set()
        packages = api.loadPackage('memphis.config', seen)
        self.assertEqual(packages, ['memphis.config'])

        packages = api.loadPackage('memphis.config', seen)
        self.assertEqual(packages, [])
