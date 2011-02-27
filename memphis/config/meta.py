"""
handler
-------
  >>> api.begin()

  >>> from zope import interface
  >>> from zope.component import getSiteManager
  >>> class ITest(interface.Interface):
  ...     pass
  >>> class Ob(object):
  ...     def __init__(self, iface):
  ...         interface.directlyProvides(self, iface)

  >>> @directives.handler(ITest)
  ... def testHandler(ob):
  ...     print 'test handler'
  ...
  >>> reGrok()

  >>> sm = getSiteManager()
  >>> s = sm.subscribers((Ob(ITest),), None)

  >>> api.commit()
  >>> s = sm.subscribers((Ob(ITest),), None)
  test handler

"""
import martian, sys, types
from zope import interface, component
from zope.interface.interface import InterfaceClass

from memphis.config import api, directives
from memphis.config.directives import adapts
from memphis.config.directives import utility
from memphis.config.directives import action

_marker = object()
_adapters = []
_modules = []
_utilities = []


class AdaptsGrokker(martian.ClassGrokker):
    martian.component(types.ObjectType)
    martian.directive(adapts)

    def execute(self, factory, configContext=api.UNSET, **kw):
        value = adapts.bind(default=_marker).get(factory)
        if value is _marker:
            return False

        for required, name, info in value:
            provided = iter(interface.implementedBy(factory)).next()

            if (factory, required, provided, name) in _adapters:
                continue
            _adapters.append((factory, required, provided, name))

            factory.__component_adapts__ = required

            api.registerAdapter(
                factory, required, provided, name, configContext, info)

        return True


class UtilityGrokker(martian.ClassGrokker):
    martian.component(types.ObjectType)
    martian.directive(utility)

    def execute(self, factory, configContext=api.UNSET, **kw):
        value = utility.bind(default=_marker).get(factory)
        if value is _marker:
            return False

        provides, name, info = value

        if (factory, provides, name) in _utilities:
            return False
        _utilities.append((factory, provides, name))

        if not provides.implementedBy(factory):
            interface.classImplements(factory, provides)

        api.registerUtility(factory(), provides, name, configContext, info)
        return True


class AdapterGrokker(martian.InstanceGrokker):
    martian.component(types.FunctionType)

    def grok(self, name, obj, configContext=api.UNSET, **kw):
        if getattr(obj, '_register_adapter', False):
            if (name, obj) in _adapters:
                return False
            _adapters.append((name, obj))

            provides = list(interface.implementedBy(obj))[0]

            for required, kwargs, info in obj._register_adapter:
                api.registerAdapter(
                    obj, required, provides, 
                    kwargs.get('name',''), configContext, info)

            return True
        else:
            return False


class HandlerGrokker(martian.InstanceGrokker):
    martian.component(types.FunctionType)

    def grok(self, name, obj, configContext=api.UNSET, **kw):
        if getattr(obj, '_register_handler', False):
            for required, info in obj._register_handler:
                api.registerHandler(obj, required, configContext, info)
            return True
        else:
            return False


class ActionGrokker(martian.GlobalGrokker):

    def grok(self, name, module, configContext=None, **kw):
        value = action.bind(default=_marker).get(module)
        if value is not _marker:
            if (name, module) in _modules:
                return False
            _modules.append((name, module))

            for callable, args, kwargs, info in value:
                kwargs = dict(kwargs)
                if 'discriminator' in kwargs:
                    discriminator = kwargs['discriminator']
                    del kwargs['discriminator']
                    api.action(configContext, discriminator,
                               callable, args, kwargs, info=info)
                    continue

                callable(*args, **kwargs)

        return True


@api.cleanup
def cleanUp():
    global _adapters, _modules, _utilities

    _modules = []
    _adapters = []
    _utilities = []
