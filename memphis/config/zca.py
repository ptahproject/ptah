""" zca configuration 

registry
--------
  >>> api.begin()

  >>> from zope import interface
  >>> from memphis.config import directives

  >>> sm1 = registry('sm1')
  >>> reg = registry('test')

  >>> getRegistry('test') is reg
  True

  >>> getRegistry() == [reg, sm1]
  True

  >>> _ = directives.registerIn('test')

  >>> class ITest(interface.Interface):
  ...     pass

  >>> class Ob(object):
  ...     def __init__(self, iface):
  ...         interface.directlyProvides(self, iface)

  >>> @directives.handler(ITest)
  ... def testHandler(ob):
  ...     print 'test handler'

  >>> reGrok()

  >>> sm = getSiteManager()
  >>> s = sm.subscribers((Ob(ITest),), None)

  >>> api.commit()
  >>> sm is getSiteManager()
  True
  >>> s = sm.subscribers((Ob(ITest),), None)

  >>> s = reg.subscribers((Ob(ITest),), None)
  test handler

  >>> f, name = reg.__reduce__()
  >>> f, name
  (<function BC at ...>, ('test',))

  >>> f(*name) is reg
  True

  >>> reGrok()

  >>> del registries['test']

  >>> f(*name)
  Broken registry: test

  >>> registerInEnd()
  >>> globalSiteManager is getSiteManager()
  True

"""
import sys, random, pkg_resources
from zope.component import globalSiteManager, getSiteManager
from zope.component.hooks import getSite, setSite
from zope.component.registry import Components
from zope.component.event import objectEventNotify
from zope.component.globalregistry import BaseGlobalComponents

from memphis.config import api, directives
from memphis.config.directives import action


@action
def registerObjectEvent():
    sm = globalSiteManager
    sm.unregisterHandler(objectEventNotify)
    sm.registerHandler(objectEventNotify)


registries = {}

def BC(name):
    bc = registries.get(name, None)
    if bc is None:
        registries[name] = BrokenRegistry(name)
        return registries[name]
    else:
        return bc


class Registry(BaseGlobalComponents):

    def __init__(self, name, title=u'', description=u'', addon=False):
        self.title = title
        self.description = description
        self.addon = addon
        self.__name__ = name
        super(Registry, self).__init__(name)

    def __reduce__(self):
        return BC, (self.__name__,)


class BrokenRegistry(BaseGlobalComponents):

    def __init__(self, name, title=u'', description=u'', addon=False):
        self.title = title
        self.description = description
        self.addon = addon
        self.__name__ = name
        super(BrokenRegistry, self).__init__(name)

    def __repr__(self):
        return "Broken registry: %s"%self.__name__


class Site(object):

    def __init__(self, sm):
        self.sm = sm

    def getSiteManager(self):
        return self.sm


stack = []

def registry(name, title=u'', description=u'', addon=False):
    sm = Registry(name)
    sm.title = title
    sm.description = description
    sm.addon = addon
    registries[name] = sm

    def complete():
        registries[name] = sm

    frame = sys._getframe(1)

    action(
        complete,
        __frame = frame,
        __info = directives.getInfo(2),
        __discriminator = ('memphis.config:registry', name),
        __order = (api.moduleNum(frame.f_locals['__name__']), 0))

    return sm


def getRegistry(name=None):
    if name is not None:
        return registries.get(name)
    return registries.values()


def registerIn(name):
    sm = registries[name]

    curr_site = getSite()
    stack.append(curr_site)

    setSite(Site(sm))


def registerInEnd():
    if not stack:
        setSite(None)
        return

    site = stack.pop()
    setSite(site)


@api.cleanup
def cleanup():
    registries.clear()
