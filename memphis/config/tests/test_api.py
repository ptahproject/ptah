""" """
import unittest
from zope import interface, component
from zope.component import getSiteManager

from memphis.config import api


class TestAPI(unittest.TestCase):

    def tearDown(self):
        getSiteManager().__init__('base')

    def test_adapter_simple(self):
        sm = getSiteManager()

        def adapter(context):
            return Adapter(context)

        self.assertRaises(
            ValueError,
            api.registerAdapter, adapter)

        self.assertRaises(
            ValueError,
            api.registerAdapter, adapter, provides=IAdapter)

        self.assertRaises(
            TypeError,
            api.registerAdapter, adapter, required=(IContext,))

        api.registerAdapter(adapter, (IContext,), IAdapter)
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is adapter)

        a = sm.getAdapter(Context(), IAdapter)
        self.assertTrue(isinstance(a, Adapter))

    def test_adapter_2(self):
        sm = getSiteManager()

        @interface.implementer(IAdapter)
        def adapter(context):
            return Adapter(context)

        api.registerAdapter(adapter, (IContext,))
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is adapter)

        a = sm.getAdapter(Context(), IAdapter)
        self.assertTrue(isinstance(a, Adapter))

    def test_adapter_3(self):
        sm = getSiteManager()

        @component.adapter(IContext)
        @interface.implementer(IAdapter)
        def adapter(context):
            return Adapter(context)

        api.registerAdapter(adapter)
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is adapter)

        a = sm.getAdapter(Context(), IAdapter)
        self.assertTrue(isinstance(a, Adapter))

    def test_adapter_4(self):
        sm = getSiteManager()

        class Adapter(object):
            component.adapts(IContext)
            interface.implements(IAdapter)

            def __init__(self, context):
                self.context = context

        api.registerAdapter(Adapter)
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is Adapter)

        a = sm.getAdapter(Context(), IAdapter)
        self.assertTrue(isinstance(a, Adapter))

    def test_utility_1(self):
        sm = getSiteManager()

        class Util(object):
            pass

        self.assertRaises(
            TypeError,
            api.registerUtility, Util)

        api.registerUtility(Util(), IContext)

        util = sm.getUtility(IContext)
        self.assertTrue(isinstance(util, Util))

    def test_utility_2(self):
        sm = getSiteManager()

        class Util(object):
            interface.implements(IContext)

        api.registerUtility(Util())

        util = sm.getUtility(IContext)
        self.assertTrue(isinstance(util, Util))

    def test_handler_1(self):
        sm = getSiteManager()

        events = []
        def handler(ev):
            events.append(ev)

        self.assertRaises(
            TypeError,
            api.registerHandler, handler)

        self.assertRaises(
            TypeError,
            api.registerHandler, handler, IContext)

        api.registerHandler(handler, (IContext,))
        api.notify(Context())
        self.assertTrue(len(events)==1)

    def test_adapter_action(self):
        sm = getSiteManager()

        @interface.implementer(IAdapter)
        def adapter(context):
            return Adapter(context)

        api.action(callable=api.registerAdapter, args=(adapter, (IContext,)))
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is adapter)

        a = sm.getAdapter(Context(), IAdapter)
        self.assertTrue(isinstance(a, Adapter))

    def test_adapter_10(self):
        api.begin()
        api.loadPackages()
        api.commit()

        grokker = api.grokkerRegistry._grokker
        m = grokker._multi_global_grokker
        print m.__dict__.items()


class IContext(interface.Interface):
    pass


class IAdapter(interface.Interface):
    pass


class Context(object):
    interface.implements(IContext)


class Adapter(object):
    interface.implements(IAdapter)

    def __init__(self, context):
        self.context = context
