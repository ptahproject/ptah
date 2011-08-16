""" directives tests """
import unittest
from zope import interface
from zope.component import getSiteManager

from memphis import config


class BaseTesting(unittest.TestCase):

    def _init_memphis(self, settings={}, *args, **kw):
        config.begin()
        config.loadPackage('memphis.config')
        config.addPackage(self.__class__.__module__)
        config.commit()

    def tearDown(self):
        config.cleanUp()


class TestAdaptsDirective(BaseTesting):

    def test_adapts(self):
        global TestClass

        class IContext(interface.Interface):
            pass

        class IAdapter(interface.Interface):
            pass

        class TestClass(object):
            config.adapts(IContext)
            config.adapts(IContext)
            interface.implements(IAdapter)

            def __init__(self, context):
                self.context = context

        self._init_memphis()

        sm = getSiteManager()
        adapters = sm.adapters.lookupAll((IContext,), IAdapter)

        self.assertTrue(len(adapters) == 1)
        self.assertTrue(adapters[0][1] is TestClass)


class Context(object):

    def __init__(self, iface):
        interface.directlyProvides(self, iface)
