""" zca configuration 

registry
--------
  >>> api.begin()

  >>> from zope import interface
  >>> from zope.component import getSiteManager

  >>> from memphis.config import directives

  >>> sm1 = registry('sm1')
  >>> def _sm1(context=None):
  ...   return sm1
  >>> _ = getSiteManager.sethook(_sm1)

  >>> reg = registry('test')

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
  (<function BC at ...>, 'test')

  >>> f(None, name) is reg
  True

  >>> del registries['test']

  >>> f(None, name)
  Broken registry

  >>> registerInEnd()
  >>> globalSiteManager is getSiteManager()
  True

"""
import random
from zope.component import globalSiteManager, getSiteManager
from zope.component.registry import Components
from zope.component.event import objectEventNotify

from memphis.config import api, directives
from memphis.config.directives import action


action(api.registerHandler, objectEventNotify)


registries = {}

def BC(components, name):
    bc = registries.get(name, None)
    if bc is None:
        return broken
    else:
        return bc


class Registry(Components):

    def __reduce__(self):
        return BC, self.__name__



class BrokenRegistry(Components):

    def __init__(self):
        self.__parent__ =  globalSiteManager
        super(BrokenRegistry, self).__init__('broken')

    def __repr__(self):
        return "Broken registry"


broken = BrokenRegistry()


stack = []

def registry(name):
    sm = Registry(name)
    registries[name] = sm
    return sm


def registerIn(name):
    sm = registries[name]
    def _sm(context=None):
        return sm

    curr_sm = getSiteManager()
    if curr_sm is not globalSiteManager:
        stack.append(getSiteManager())

    getSiteManager.sethook(_sm)


def registerInEnd():
    if not stack:
        getSiteManager.reset()
        return

    sm = stack.pop()
    def _sm(context=None):
        return sm

    getSiteManager.sethook(_sm)


def _finalizeModule(name, mod, kw, _marker=object()):
    value = directives.registerIn.bind(default=_marker).get(mod)
    if value is not _marker:
        api.action(
            discriminator='registerInEnd: %s'%random.randint(1, 99999),
            callable=registerInEnd)


api.grokkerRegistry.finalize = _finalizeModule
