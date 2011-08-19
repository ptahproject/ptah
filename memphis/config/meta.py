import martian, sys, types, random
from zope import interface, component
from zope.interface.interface import InterfaceClass

from memphis.config import api, zca, directives
from memphis.config.directives import adapts
from memphis.config.directives import utility
from memphis.config.directives import action
from memphis.config.directives import registerIn

_marker = object()


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
                factory, required, provided, name, configContext, 
                (api.moduleNum(factory.__module__), 220), info)

        return True


class UtilityGrokker(martian.ClassGrokker):
    martian.component(types.ObjectType)
    martian.directive(utility)

    def execute(self, factory, configContext=api.UNSET, **kw):
        value = utility.bind(default=_marker).get(factory)
        if value is _marker:
            return False

        provides, name, info = value

        if not provides.implementedBy(factory):
            interface.classImplements(factory, provides)

        comp = factory()
        api.registerUtility(comp, provides, name, configContext, 
                            (api.moduleNum(comp.__module__), 230), info)
        return True


class AdapterGrokker(martian.InstanceGrokker):
    martian.component(types.FunctionType)

    def grok(self, name, obj, configContext=api.UNSET, **kw):
        if getattr(obj, '_register_adapter', False):
            try:
                provides = list(interface.implementedBy(obj))[0]
            except IndexError:
                raise ValueError("Can't find provided interfaec")

            for required, kwargs, info in obj._register_adapter:
                api.registerAdapter(
                    obj, required, provides,
                    kwargs.get('name',''), configContext, 
                    (api.moduleNum(obj.__module__), 220), info)
            return True
        else:
            return False


class HandlerGrokker(martian.InstanceGrokker):
    martian.component(types.FunctionType)

    def grok(self, name, obj, configContext=api.UNSET, **kw):
        if getattr(obj, '_register_handler', False):
            for required, info in obj._register_handler:
                api.registerHandler(
                    obj, required, configContext, 
                    (api.moduleNum(obj.__module__), 210), info)
            return True
        else:
            return False


class ActionGrokker(martian.GlobalGrokker):

    def grok(self, name, module, configContext=api.UNSET, **kw):
        value = action.bind(default=_marker).get(module)
        if value is not _marker:
            if (name, module) not in _modules or \
                    getattr(module, '__fake_module__', False):
                _modules.append((name, module))

                for callable, args, kwargs, info in value:
                    kwargs = dict(kwargs)
                    if '__discriminator' in kwargs:
                        order = 0
                        discriminator = kwargs['__discriminator']
                        del kwargs['__discriminator']
                        if '__order' in kwargs:
                            order = kwargs['__order']
                            del kwargs['__order']

                        api.action(
                            configContext, discriminator,
                            callable, args, kwargs, order=order, info=info)
                    else:
                        callable(*args, **kwargs)

        return True


class RegisterInGrokker(martian.GlobalGrokker):

    def grok(self, name, module, configContext=api.UNSET, **kw):
        value = registerIn.bind(default=_marker).get(module)
        if value is not _marker:
            if (name, module) not in _rmodules or \
                    getattr(module, '__fake_module__', False):
                _rmodules.append((name, module))

                id = random.randint(1, 99999)
                name, info = value
                api.action(
                    configContext,
                    discriminator='registerIn: %s'%id,
                    callable=zca.registerIn, args=(name,),
                    order = (api.moduleNum(module.__name__), 9),
                    info = info
                    )

                api.action(
                    configContext,
                    discriminator='registerInEnd: %s'%id,
                    callable=zca.registerInEnd,
                    order = (api.moduleNum(module.__name__), 999999999),
                    )

        return True


_adapters = []
_modules = []
_rmodules = []

@api.cleanup
def cleanUp():
    global _adapters, _modules, _rmodules, _utilities

    names = (action.dotted_name(), registerIn.dotted_name())
    for n, mod in _modules + _rmodules:
        for name in names:
            if hasattr(mod, name):
                delattr(mod, name)

    _modules = []
    _rmodules = []
    _adapters = []
