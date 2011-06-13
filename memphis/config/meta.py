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

action
------

  >>> api.begin()
  >>> def actionMeth():
  ...     print 'actionMeth'

  >>> def wrongScope():
  ...     action(actionMeth)

  >>> wrongScope()
  Traceback (most recent call last):
  ...
  GrokImportError: The 'action' directive can only be used on module level.

  >>> action(actionMeth)
  <memphis.config.directives.action ...>

  >>> action.immediately = True
  >>> action(actionMeth)
  actionMeth
  <memphis.config.directives.action ...>

  >>> import sys
  >>> frame = sys._getframe(0)

  >>> def differentScope():
  ...     action(actionMeth, __frame=frame)

  >>> differentScope()
  actionMeth

  >>> action.immediately = False

"""
import martian, sys, types, random
from zope import interface, component
from zope.interface.interface import InterfaceClass

from memphis.config import api, zca, directives
from memphis.config.directives import adapts
from memphis.config.directives import utility
from memphis.config.directives import action
from memphis.config.directives import registerIn

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
            if (name, module) not in _modules or \
                    getattr(module, '__fake_module__', False):
                _modules.append((name, module))

                for callable, args, kwargs, info in value:
                    kwargs = dict(kwargs)
                    if 'discriminator' in kwargs:
                        discriminator = kwargs['discriminator']
                        del kwargs['discriminator']
                        if 'actionOrder' in kwargs:
                            order = kwargs['actionOrder']
                            del kwargs['actionOrder']
                        else:
                            order = 0
                        api.action(
                            configContext, discriminator,
                            callable, args, kwargs, order=order, info=info)
                        continue
                
                    callable(*args, **kwargs)

        return True


class RegisterInGrokker(martian.GlobalGrokker):

    def grok(self, name, module, configContext=None, **kw):
        value = registerIn.bind(default=_marker).get(module)
        if value is not _marker:
            if (name, module) not in _modules or \
                    getattr(module, '__fake_module__', False):
                _modules.append((name, module))

                api.action(
                    discriminator='registerIn: %s'%random.randint(1, 99999),
                    callable=zca.registerIn, args=(value,))

        return True


@api.cleanup
def cleanUp():
    global _adapters, _modules, _utilities

    _modules = []
    _adapters = []
    _utilities = []
