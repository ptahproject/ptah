""" """
import sys, unittest
from zope import interface
from zope.component.hooks import getSite
from zope.component import queryUtility, getSiteManager
from zope.component.globalregistry import BaseGlobalComponents

from memphis import config
from memphis.config import zca, meta


class TestZCA(unittest.TestCase):

    def tearDown(self):
        config.cleanUp()

    def test_zca_registry(self):
        sm = zca.registry('test')

        self.assertTrue(isinstance(sm, BaseGlobalComponents))
        self.assertTrue(zca.getRegistry('test') is sm)
        self.assertTrue(zca.BC('test') is sm)
        self.assertEqual(zca.getRegistry(), [sm])

        config.begin()
        config.loadPackages()
        config.commit()

    def test_zca_broken(self):
        sm = zca.BC('unknown')

        self.assertTrue(isinstance(sm, zca.BrokenRegistry))
        self.assertEqual(repr(sm), 'Broken registry: unknown')

    def test_zca_registerIn(self):
        class IUtility(interface.Interface):
            pass
        class Utility(object):
            interface.implements(IUtility)

        sm = zca.registry('test')

        self.assertTrue(sm.__reduce__(),
                        (zca.BC, ('test',)))
        
        zca.registerIn('test')

        site = getSite()
        self.assertTrue(site.getSiteManager() is sm)

        siteManager = site.getSiteManager()
        siteManager.registerUtility(Utility())
        self.assertTrue(siteManager.getUtility(IUtility) is not None)

        zca.registerInEnd()

        self.assertTrue(queryUtility(IUtility) is None)

    def test_zca_registerIn_stack(self):
        sm1 = zca.registry('test1')
        sm2 = zca.registry('test2')
        
        zca.registerIn('test1')
        site = getSite()
        self.assertTrue(site.getSiteManager() is sm1)

        zca.registerIn('test2')
        site = getSite()
        self.assertTrue(site.getSiteManager() is sm2)

        zca.registerInEnd()

        site = getSite()
        self.assertTrue(site.getSiteManager() is sm1)
        
        zca.registerInEnd()

        site = getSite()
        self.assertTrue(site is None)

        zca.registerInEnd()

    def test_zca_register_grokker(self):
        config.cleanUp()
        sm = zca.registry('test')
        #config.registerIn('test')
        
        name = self.__class__.__module__
        mod = sys.modules[name]

        #config.begin()
        #config.loadPackages()
        #config.commit()

        #print mod
        #meta.RegisterInGrokker().grok(name, mod)
        #for i in mod.__dict__['memphis.config.directives.action']:
        #    print i
